#include "run_io.hpp"
#include "ts808/linear_response.hpp"
#include <fstream>
#include <iostream>
#include <cfenv>
int main(int argc,char** argv){
    using namespace ts808;using namespace ts808::offline;
    if(argc!=5||std::string(argv[1])!="--case"||std::string(argv[3])!="--output"){std::cerr<<"Usage: ts808_offline --case case.json --output new-directory\n";return 10;}
    Case c;Model model;
    try{c=read_case(argv[2]);const auto status=model.prepare({},c.controls,c.settings);if(!status.ok||std::fegetround()!=FE_TONEAREST)throw std::invalid_argument("Invalid core configuration or rounding mode");}
    catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 10;}
    try{
        const std::filesystem::path directory=argv[4];if(!std::filesystem::create_directory(directory))throw std::runtime_error("Output directory already exists");
        const auto& d=c.document;const std::string run_id=d.at("case_id").get<std::string>()+"-"+std::to_string(c.settings.rate_Hz);
        Json columns=Json::array({{{"id","time"},{"quantity","time"},{"unit","s"},{"orientation","origin + index/rate"}}});
        for(int i=0;i<31;++i)columns.push_back({{"id",unknown_names[i]},{"quantity",is_current(i)?"branch_current":is_state(i)?"state":"node_voltage"},{"unit",is_current(i)?"A":"V"},{"orientation",is_current(i)?"component-map segment orientation":"relative to gnd"}});
        Json run={{"schema_version",1},{"run_id",run_id},{"case_id",d.at("case_id")},{"model_id","ts808-cerutti-reduced-v1"},{"physical_case_sha256",d.at("physical_case_sha256")},{"case_input_sha256",nullptr},
            {"execution_config",d.at("execution")},{"build",{{"compiler",__VERSION__},{"flags","-O2 -fno-fast-math -ffp-contract=off"},{"precision","binary64"},{"eigen","5.0.1"}}},
            {"reference_identity",nullptr},{"trace",{{"filename","traces.f64le"},{"dtype","<f8"},{"order","C"},{"shape",{0,32}},{"columns",columns},{"byte_length",0},{"integrity","pending"},{"sha256",nullptr}}},
            {"completion",{{"state","incomplete"},{"requested_samples",c.samples},{"written_samples",0}}},{"diagnostics",Json::object()}};
        run["execution_config"]["ordered_unknowns"]=unknown_names;run["execution_config"]["interior_counts"]={4,6,11,5};run["execution_config"]["boundary_count"]=5;run["execution_config"]["unknown_count"]=31;
        write_json(directory/"run.json",run);std::ofstream trace(directory/"traces.f64le",std::ios::binary);
        auto dc=model.initialize_dc(0);Status status=dc.status;std::uint64_t written=0;double switch_max=0;
        if(status.ok){write_row(trace,0,model.state());written=1;switch_max=std::abs(model.state()[wet_send]-model.state()[switch_common]);}
        for(std::uint64_t sample=1;status.ok&&sample<c.samples;++sample){
            const double time=static_cast<double>(sample)/c.settings.rate_Hz;
            const auto step=model.advance(stimulus(d.at("stimulus"),time));status=step.status;if(!status.ok)break;
            write_row(trace,time,model.state());++written;switch_max=std::max(switch_max,std::abs(model.state()[wet_send]-model.state()[switch_common]));
        }
        trace.close();if(!trace)throw std::runtime_error("Cannot close trace");
        if(status.ok&&d.at("analysis_kind")=="ac"){
            const auto frequencies=d.at("analysis").at("frequencies_Hz").get<std::vector<double>>();std::vector<ComplexResponse> continuous(frequencies.size()),discrete(frequencies.size());
            status=linear_response({},c.controls,model.state(),c.settings,frequencies,continuous,discrete);
            if(status.ok){std::ofstream response(directory/"response.f64le",std::ios::binary);
                for(std::size_t i=0;i<frequencies.size();++i){const std::array<double,5> row={frequencies[i],continuous[i].real(),continuous[i].imag(),discrete[i].real(),discrete[i].imag()};write_values(response,row);}
                response.close();if(!response)throw std::runtime_error("AC response write failed");
                run["response"]={{"filename","response.f64le"},{"dtype","<f8"},{"order","C"},{"shape",{301,5}},{"columns",{"frequency_Hz","continuous_real","continuous_imag","discrete_real","discrete_imag"}},{"byte_length",301*5*8},{"integrity","pending"},{"sha256",nullptr}};}

        }
        run["completion"]["state"]=status.ok?"completed":"failed";run["completion"]["written_samples"]=written;run["trace"]["shape"]={written,32};run["trace"]["byte_length"]=written*256;
        run["diagnostics"]=diagnostics(status.diagnostics);run["diagnostics"]["wet_switch_voltage_max_abs_V"]={{"value",written?Json(switch_max):Json(nullptr)},{"available",written>0},{"coverage",status.ok?"complete":"partial"}};
        if(!status.ok)write_json(directory/"failure.json",{{"schema_version",1},{"run_id",run_id},{"case_id",d.at("case_id")},{"physical_case_sha256",d.at("physical_case_sha256")},{"stage",written?"transient":"DC"},{"reason",run["diagnostics"]["reason"]},{"failed_sample_index",written},{"failed_time_s",static_cast<double>(written)/c.settings.rate_Hz},{"last_valid_state_id",written?Json(run_id+":"+std::to_string(written-1)):Json(nullptr)},{"diagnostics",run["diagnostics"]}});
        write_json(directory/"run.json",run);return status.ok?0:written?21:20;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 50;}
}
