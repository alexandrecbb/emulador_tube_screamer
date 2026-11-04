#include "ts808/model.hpp"
#include <cmath>
namespace ts808 {
Status Model::prepare(const PreparedParameters& p,const Controls& c,const NumericalSettings& s) noexcept {
    prepared_=initialized_=failed_=false;index_=0;
    auto positive=[](double v){return std::isfinite(v)&&v>0;};
    auto fraction=[](double v){return std::isfinite(v)&&v>=0&&v<=1;};
    const auto& o=p.opamp;const auto& b=p.bjt;
    bool valid=s.row_scaling==NumericalSettings::RowScaling::max_abs_after_physical&&fraction(c.drive)&&fraction(c.tone)&&fraction(c.volume)&&p.supply==9&&p.temperature==298.15&&
        (s.rate_Hz==192000||s.rate_Hz==384000||s.rate_Hz==768000)&&s.max_newton_dc<=100&&s.max_newton_transient<=32&&
        s.max_line_search>=1&&s.max_line_search<=9;
    for(double v:{p.diode.Is,p.diode.n,b.Is,b.BF,b.BR,b.NF,b.NR,o.A0,o.GBW,o.SR,o.Rid,o.Ro,o.tau,
        o.headroom_plus,o.headroom_minus,o.W_plus,o.W_minus,p.drive_total,p.tone_total,p.volume_total,
        s.atol_current_A,s.atol_voltage_V,s.rtol_residual,s.atol_increment_current_A,s.atol_increment_voltage_V,
        s.rtol_increment,s.voltage_scale_V,s.current_scale_A,s.pivot_epsilon_factor,s.minimum_rcond,s.maximum_backward_error,s.maximum_schur_difference})valid&=positive(v);
    valid&=std::isfinite(o.bias_plus)&&std::isfinite(o.bias_minus)&&std::isfinite(o.offset)&&
        o.headroom_plus+o.W_plus<p.supply/2&&o.headroom_minus+o.W_minus<p.supply/2&&
        s.armijo_c1>0&&s.armijo_c1<1&&s.minimum_rcond<=1;
    const PreparedParameters nominal;
    for(int i=0;i<22;++i)valid&=positive(p.resistors[i].value)&&p.resistors[i].a==nominal.resistors[i].a&&p.resistors[i].b==nominal.resistors[i].b;
    for(int i=0;i<12;++i)valid&=positive(p.capacitors[i].value)&&p.capacitors[i].a==nominal.capacitors[i].a&&p.capacitors[i].b==nominal.capacitors[i].b;
    if(!valid){auto status=failure(FailureReason::invalid_configuration,SolveStage::configuration);diagnostics_=status.diagnostics;return status;}
    parameters_=p;controls_=c;settings_=s;history_={};state_.setZero();diagnostics_={};prepared_=true;return {};
}
DcResult Model::initialize_dc(double source) noexcept {
    if(!prepared_)return {failure(FailureReason::not_prepared,SolveStage::dc),0};
    if(failed_)return {{false,diagnostics_},diagnostics_.iterations};
    StateVector candidate=dc_initial_guess();CommittedHistory empty{};
    auto status=newton(candidate,source,empty,parameters_,controls_,settings_,SolveMode::dc);
    diagnostics_=status.diagnostics;
    if(!status.ok){failed_=true;return {status,status.diagnostics.iterations};}
    state_=candidate;history_={};
    for(int i=0;i<12;++i){const auto& cap=parameters_.capacitors[i];history_.capacitors[i].voltage_V=
        node_voltage(cap.a,state_,source,parameters_)-node_voltage(cap.b,state_,source,parameters_);}
    history_.previous_z={state_[z_clip],state_[z_tone]};initialized_=true;index_=0;
    return {status,status.diagnostics.iterations};
}
StepResult Model::advance(double source) noexcept {
    if(failed_)return {{false,diagnostics_},index_,0,false};
    if(!prepared_)return {failure(FailureReason::not_prepared,SolveStage::transient),index_,0,false};
    if(!initialized_)return {failure(FailureReason::not_initialized,SolveStage::transient),index_,0,false};
    if(index_==std::numeric_limits<std::uint64_t>::max()){
        failed_=true;auto s=failure(FailureReason::invalid_grid,SolveStage::transient);diagnostics_=s.diagnostics;return {s,index_,0,false};}
    StateVector candidate=state_;
    auto status=newton(candidate,source,history_,parameters_,controls_,settings_,SolveMode::transient);
    diagnostics_=status.diagnostics;
    if(!status.ok){diagnostics_.failed_sample_index=index_+1;status.diagnostics=diagnostics_;failed_=true;return {status,index_,0,false};}
    CommittedHistory next=history_;
    for(int i=0;i<12;++i){const auto& cap=parameters_.capacitors[i];const double voltage=
        node_voltage(cap.a,candidate,source,parameters_)-node_voltage(cap.b,candidate,source,parameters_);
        next.capacitors[i]={voltage,2*cap.value*settings_.rate_Hz*(voltage-history_.capacitors[i].voltage_V)-history_.capacitors[i].current_A};}
    next.previous_z={candidate[z_clip],candidate[z_tone]};
    next.opamp_derivatives={opamp_state(candidate[clip_plus]-candidate[clip_minus]+parameters_.opamp.offset,candidate[z_clip],parameters_.opamp,parameters_.supply).value,
        opamp_state(candidate[tone_in]-candidate[tone_minus]+parameters_.opamp.offset,candidate[z_tone],parameters_.opamp,parameters_.supply).value};
    state_=candidate;history_=next;++index_;return {status,index_,state_[output],true};
}
}
