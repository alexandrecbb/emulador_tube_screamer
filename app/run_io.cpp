#include "run_io.hpp"
#include <bit>
#include <cmath>
#include <fstream>
#include <numbers>
#include <set>
#include <stdexcept>
#if NLOHMANN_JSON_VERSION_MAJOR != 3 || NLOHMANN_JSON_VERSION_MINOR != 12 || NLOHMANN_JSON_VERSION_PATCH != 0
#error nlohmann_json_3_12_0_required
#endif
namespace ts808::offline {
namespace {
void keys(const Json& j,std::initializer_list<const char*> expected){
    if(!j.is_object()||j.size()!=expected.size())throw std::invalid_argument("Object keys mismatch");
    for(auto key:expected)if(!j.contains(key))throw std::invalid_argument("Missing required key");
}
double number(const Json& j,const char* key){const auto& value=j.at(key);
    if(!value.is_number()||!std::isfinite(value.get<double>()))throw std::invalid_argument("Expected a finite number");return value.get<double>();}
std::uint32_t integer(const Json& j,const char* key){const auto& value=j.at(key);
    if(!value.is_number_unsigned()||value.get<std::uint64_t>()>UINT32_MAX)throw std::invalid_argument("Expected uint32");return value.get<std::uint32_t>();}
}
Case read_case(const std::filesystem::path& path){
    std::ifstream stream(path);if(!stream)throw std::runtime_error("Cannot open case");Case c;
    stream>>c.document;const auto& d=c.document;
    keys(d,{"schema_version","case_id","physical_case_sha256","physical_descriptor","analysis_kind","circuit","stimulus","analysis","execution","trace_columns"});
    if(integer(d,"schema_version")!=1)throw std::invalid_argument("Unsupported version");
    const auto& circuit=d.at("circuit");keys(circuit,{"model_id","component_map_sha256","device_spec_sha256","controls","supply_V","temperature_K","source_Ohm","load_Ohm","R_on_Ohm"});
    if(circuit.at("model_id")!="ts808-cerutti-reduced-v1"||number(circuit,"supply_V")!=9||number(circuit,"temperature_K")!=298.15||number(circuit,"source_Ohm")!=1000||number(circuit,"load_Ohm")!=1e6||number(circuit,"R_on_Ohm")!=383.29731360711594)throw std::invalid_argument("Incompatible circuit");
    const auto& controls=circuit.at("controls");keys(controls,{"drive","tone","volume"});
    c.controls={number(controls,"drive"),number(controls,"tone"),number(controls,"volume")};
    const auto& execution=d.at("execution");keys(execution,{"rate_Hz","formulation_id","solver","purpose"});
    c.settings.rate_Hz=integer(execution,"rate_Hz");
    if(execution.at("formulation_id")!="control-branch-v1"||(execution.at("purpose")!="target"&&execution.at("purpose")!="pilot")||
        (c.settings.rate_Hz==768000&&execution.at("purpose")!="pilot"))throw std::invalid_argument("Invalid execution");
    const auto& s=execution.at("solver");
    keys(s,{"atol_current_A","atol_voltage_V","rtol_residual","atol_increment_current_A","atol_increment_voltage_V","rtol_increment","max_newton_dc","max_newton_transient","max_line_search","armijo_c1","voltage_scale_V","current_scale_A","pivot_epsilon_factor","minimum_rcond","maximum_backward_error","maximum_schur_difference","row_scaling"});
#define VALUE(field) c.settings.field=number(s,#field)
    VALUE(atol_current_A);VALUE(atol_voltage_V);VALUE(rtol_residual);VALUE(atol_increment_current_A);
    VALUE(atol_increment_voltage_V);VALUE(rtol_increment);VALUE(armijo_c1);VALUE(voltage_scale_V);
    VALUE(current_scale_A);VALUE(pivot_epsilon_factor);VALUE(minimum_rcond);VALUE(maximum_backward_error);VALUE(maximum_schur_difference);
#undef VALUE
    c.settings.max_newton_dc=integer(s,"max_newton_dc");c.settings.max_newton_transient=integer(s,"max_newton_transient");c.settings.max_line_search=integer(s,"max_line_search");
    if(s.at("row_scaling")!="max_abs_after_physical")throw std::invalid_argument("Unsupported row scaling");
    if(!d.at("case_id").is_string()||d.at("case_id").get<std::string>().find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789_-.")!=std::string::npos||d.at("case_id").get<std::string>().empty())throw std::invalid_argument("Invalid case ID");
    for(const auto* hash:{"component_map_sha256","device_spec_sha256"}){
        auto str=circuit.at(hash).get<std::string>();if(str.size()!=64||str.find_first_not_of("0123456789abcdef")!=std::string::npos)throw std::invalid_argument("Invalid hash");}
    const auto hash=d.at("physical_case_sha256").get<std::string>();if(hash.size()!=64||hash.find_first_not_of("0123456789abcdef")!=std::string::npos)throw std::invalid_argument("Invalid physical hash");
    const auto& trace=d.at("trace_columns");if(!trace.is_array()||trace.size()!=32||trace[0]!="time")throw std::invalid_argument("Invalid traces");
    for(int i=0;i<31;++i)if(trace[i+1]!=unknown_names[i])throw std::invalid_argument("Trace ordering mismatch");
    const auto kind=d.at("analysis_kind").get<std::string>();const auto& analysis=d.at("analysis");
    if(kind=="transient"){
        keys(analysis,{"time","windows","required_checks"});const auto& time=analysis.at("time");keys(time,{"origin_s","duration_s","sample_count"});
        const double duration=number(time,"duration_s");if(number(time,"origin_s")!=0||duration<=0)throw std::invalid_argument("Invalid time domain");
        if(!time.at("sample_count").is_number_unsigned())throw std::invalid_argument("Invalid sample count");
        c.samples=time.at("sample_count").get<std::uint64_t>();
        const double intervals=duration*c.settings.rate_Hz;
        if(intervals>static_cast<double>(UINT64_MAX/256-1)||std::floor(intervals)!=intervals||c.samples!=static_cast<std::uint64_t>(intervals)+1)throw std::invalid_argument("Grid/count mismatch");
    }else if(kind=="dc"||kind=="ac"){
        if(kind=="dc")keys(analysis,{"windows","required_checks"});else keys(analysis,{"windows","required_checks","frequencies_Hz"});
        c.samples=1;
        if(kind=="ac"){const auto& freq=analysis.at("frequencies_Hz");if(!freq.is_array()||freq.size()!=301)throw std::invalid_argument("Invalid frequency count");
            for(int k=0;k<=300;++k){if(!freq[k].is_number()||std::abs(freq[k].get<double>()-20*std::pow(10.,k/100.))>1e-10)throw std::invalid_argument("Invalid frequency grid");}}
    }else throw std::invalid_argument("Invalid analysis kind");
    const Json expected_time=kind=="transient"?Json{{"origin_s",0.},{"duration_s",analysis.at("time").at("duration_s")}}:Json(nullptr);
    const Json expected={{"analysis_kind",kind},{"circuit",circuit},{"stimulus",d.at("stimulus")},{"time",expected_time},{"windows",analysis.at("windows")}};
    if(d.at("physical_descriptor")!=expected)throw std::invalid_argument("Physical descriptor mismatch");
    const std::string id=d.at("case_id");Json required;
    if(kind=="dc")required={"dc_voltages"};
    else if(kind=="ac")required={"bode"};
    else if(id.starts_with("linear_"))required={"linearity"};
    else if(id.starts_with("mute_"))required={"null"};
    else if(id=="hold_center")required={"dc_hold"};
    else if(id.starts_with("overload_"))required={"local_windows","recovery"};
    else if(id=="listen_high")required={"null","wav","abx"};
    else if(id.starts_with("tone_"))required={"null","harmonics","thd","settling","local_windows"};
    else throw std::invalid_argument("Unknown case family");
    if(analysis.at("required_checks")!=required)throw std::invalid_argument("Required checks cannot be disabled");
    // Validate the analytic stimulus at the origin before creating output artifacts.
    if(stimulus(d.at("stimulus"),0)!=0)throw std::invalid_argument("Baseline requires zero source at origin");
    return c;
}
double stimulus(const Json& s,double t){
    const auto kind=s.at("type").get<std::string>();
    if(kind=="dc"){keys(s,{"type","dc_V"});return number(s,"dc_V");}
    if(kind=="ac_small_signal"){keys(s,{"type","dc_V","ac_V"});if(number(s,"ac_V")!=1)throw std::invalid_argument("Unit AC required");return number(s,"dc_V");}
    auto ramp=[](double u,double duration){return u<=0?0:u>=duration?1:.5*(1-std::cos(std::numbers::pi*u/duration));};
    if(kind=="tone"||kind=="overload"){
        if(kind=="tone")keys(s,{"type","frequency_Hz","peak_V","phase_rad","onset_s","rise_s"});
        else keys(s,{"type","frequency_Hz","peak_V","phase_rad","onset_s","duration_s","rise_s","fall_s"});
        const double f=number(s,"frequency_Hz"),amp=number(s,"peak_V"),rise=number(s,"rise_s"),u=t-number(s,"onset_s");
        if(f<=0||amp<=0||rise<=0||number(s,"phase_rad")!=0)throw std::invalid_argument("Invalid tone");
        double envelope=ramp(u,rise);
        if(kind=="overload"){const double duration=number(s,"duration_s"),fall=number(s,"fall_s");if(duration<=rise||fall<=0||fall>=duration)throw std::invalid_argument("Invalid burst");envelope*=ramp(duration-u,fall);}
        return amp*envelope*std::sin(2*std::numbers::pi*f*t);
    }
    if(kind=="listening"){
        keys(s,{"type","onsets_s","frequencies_Hz","note_duration_s","decay_s","coefficient_V","harmonic_coefficients","phase_rad","rise_s","fall_s"});
        if(s.at("onsets_s")!=Json::array({.1,1.1,2.1})||s.at("frequencies_Hz")!=Json::array({110.,220.,440.})||s.at("harmonic_coefficients")!=Json::array({1.,.3,.1})||number(s,"note_duration_s")!=.8||number(s,"decay_s")!=.25||number(s,"coefficient_V")!=.5/1.4||number(s,"phase_rad")!=0||number(s,"rise_s")!=.005||number(s,"fall_s")!=.005)throw std::invalid_argument("Invalid listening source");
        double result=0;for(int k=0;k<3;++k){const double u=t-s.at("onsets_s")[k].get<double>(),f=s.at("frequencies_Hz")[k].get<double>();
            if(u>=0&&u<=.8)result+=(.5/1.4)*std::exp(-u/.25)*ramp(u,.005)*ramp(.8-u,.005)*(std::sin(2*std::numbers::pi*f*u)+.3*std::sin(4*std::numbers::pi*f*u)+.1*std::sin(6*std::numbers::pi*f*u));}
        return result;
    }
    throw std::invalid_argument("Unknown stimulus");
}
void write_values(std::ostream& out,std::span<const double> values){
    for(double value:values){if(!std::isfinite(value))throw std::runtime_error("Nonfinite trace");
        const auto bits=std::bit_cast<std::uint64_t>(value);std::array<char,8> bytes;
        for(int k=0;k<8;++k)bytes[k]=static_cast<char>((bits>>(8*k))&255);
        out.write(bytes.data(),8);}
    if(!out)throw std::runtime_error("Trace write failed");
}
void write_row(std::ostream& out,double time,const StateVector& state){
    std::array<double,32> row;row[0]=time;for(int i=0;i<31;++i)row[i+1]=state[i];write_values(out,row);
}
Json diagnostics(const NumericalDiagnostics& d){
    auto scalar=[](AvailableScalar v){return Json{{"value",v.available?Json(v.value):Json(nullptr)},{"available",v.available}};};
    constexpr const char* reasons[]={"none","invalid_configuration","not_prepared","not_initialized","nonfinite_trial","singular_internal","ill_conditioned_internal","singular_boundary","ill_conditioned_boundary","linear_backward_error","non_descent_direction","line_search_exhausted","newton_budget_exhausted","invalid_grid"};
    return {{"reason",reasons[static_cast<int>(d.reason)]},{"iterations",d.iterations},{"trials",d.trials},{"block",d.block},{"row",d.row},{"rank",d.rank},{"rcond",scalar(d.rcond)},{"backward_error",scalar(d.backward_error)},{"residual_norm",scalar(d.residual_norm)},{"increment_norm",scalar(d.increment_norm)}};
}
void write_json(const std::filesystem::path& path,const Json& j){
    const auto temp=path.string()+".tmp";std::ofstream out(temp);if(!out)throw std::runtime_error("Cannot write metadata");out<<j.dump(2)<<'\n';out.close();if(!out)throw std::runtime_error("Metadata write failed");std::filesystem::rename(temp,path);
}
}
