#include "ts808/stages.hpp"
#include <cmath>
#include <numbers>
namespace ts808 {
double node_voltage(int n,const StateVector& x,double source,const PreparedParameters& p) noexcept {
    return n>=0?x[n]:n==v9?p.supply:n==generator?source:0;
}
Status assemble(const StateVector& x,double source,const CommittedHistory& hist,
    const PreparedParameters& p,const Controls& c,const NumericalSettings& settings,
    SolveMode mode,Evaluation& a) noexcept {
    a.residual.setZero(); a.contributions.setZero(); a.jacobian.setZero();
    auto v=[&](int n){return node_voltage(n,x,source,p);};
    auto add=[&](int row,double value){if(row>=0){a.residual[row]+=value;a.contributions[row]+=std::abs(value);}};
    auto jac=[&](int r,int col,double value){if(r>=0&&col>=0)a.jacobian(r,col)+=value;};
    auto branch=[&](int n,int m,double current,double conductance){
        add(n,current);add(m,-current);jac(n,n,conductance);jac(n,m,-conductance);
        jac(m,n,-conductance);jac(m,m,conductance);
    };
    for(const auto& r:p.resistors)branch(r.a,r.b,(v(r.a)-v(r.b))/r.value,1/r.value);
    if(mode==SolveMode::transient)for(int k=0;k<12;++k){
        const auto& cap=p.capacitors[k];const auto& old=hist.capacitors[k];
        const double g=2*cap.value*settings.rate_Hz;
        branch(cap.a,cap.b,g*(v(cap.a)-v(cap.b)-old.voltage_V)-old.current_A,g);
    }
    auto segment=[&](int n,int m,int i,double resistance){
        add(n,x[i]);add(m,-x[i]);jac(n,i,1);jac(m,i,-1);
        add(i,v(n));add(i,-v(m));add(i,-resistance*x[i]);
        jac(i,n,1);jac(i,m,-1);jac(i,i,-resistance);
    };
    segment(drive_end,clip_out,i_drive,p.drive_total*c.drive);
    segment(tone_in,tone_wiper,i_tone_low,p.tone_total*c.tone);
    segment(tone_wiper,tone_minus,i_tone_high,p.tone_total*(1-c.tone));
    segment(vref,wet_send,i_volume_low,p.volume_total*c.volume);
    segment(wet_send,volume_top,i_volume_high,p.volume_total*(1-c.volume));
    const double vt=thermal_voltage(p.temperature);
    for(const auto& nodes:std::array<std::array<int,2>,2>{{{clip_minus,clip_out},{clip_out,clip_minus}}}){
        const auto d=diode(v(nodes[0])-v(nodes[1]),p.diode,vt);branch(nodes[0],nodes[1],d.current,d.conductance);
    }
    for(const auto& nodes:std::array<std::array<int,3>,2>{{{v9,input_base,input_emitter},{v9,output_base,output_emitter}}}){
        const int nc=nodes[0],nb=nodes[1],ne=nodes[2];
        const auto q=bjt(v(nb)-v(ne),v(nb)-v(nc),p.bjt,vt);
        const std::array<double,3> currents={q.collector,q.base,q.emitter};
        const std::array<std::array<double,2>,3> derivatives={q.dc,q.db,q.de};
        for(int k=0;k<3;++k){add(nodes[k],currents[k]);
            jac(nodes[k],nb,derivatives[k][0]+derivatives[k][1]);
            jac(nodes[k],ne,-derivatives[k][0]);jac(nodes[k],nc,-derivatives[k][1]);}
    }
    int channel=0;
    for(const auto& nodes:std::array<std::array<int,4>,2>{{{clip_plus,clip_minus,clip_out,z_clip},{tone_in,tone_minus,tone_out,z_tone}}}){
        const int plus=nodes[0],minus=nodes[1],out=nodes[2],z=nodes[3];const auto& op=p.opamp;
        branch(plus,minus,(v(plus)-v(minus))/op.Rid,1/op.Rid);
        add(plus,op.bias_plus);add(minus,op.bias_minus);
        const auto sat=saturation(x[z],op,p.supply);
        add(out,(v(out)-(p.supply/2+sat.value))/op.Ro);
        jac(out,out,1/op.Ro);jac(out,z,-sat.derivative/op.Ro);
        const auto law=opamp_state(v(plus)-v(minus)+op.offset,x[z],op,p.supply);
        if(mode==SolveMode::dc){
            const double omega=2*std::numbers::pi*op.GBW/op.A0;
            a.residual[z]=law.value/omega;
            a.contributions[z]=std::abs(op.A0*(v(plus)-v(minus)+op.offset))+std::abs(x[z])+
                std::abs((x[z]-sat.value)/(omega*op.tau));
            jac(z,plus,law.de/omega);jac(z,minus,-law.de/omega);jac(z,z,law.dz/omega);
        }else{
            const double h2=.5/settings.rate_Hz;
            add(z,x[z]);add(z,-hist.previous_z[channel]);add(z,-h2*law.value);
            add(z,-h2*hist.opamp_derivatives[channel]);
            jac(z,z,1-h2*law.dz);jac(z,plus,-h2*law.de);jac(z,minus,h2*law.de);
        }
        ++channel;
    }
    if(!x.allFinite()||!std::isfinite(source)||!a.residual.allFinite()||!a.jacobian.allFinite()||!a.contributions.allFinite())
        return failure(FailureReason::nonfinite_trial,mode==SolveMode::dc?SolveStage::dc:SolveStage::transient);
    return {};
}
Status evaluate_residual(const StateVector& x,double s,const CommittedHistory& h,const PreparedParameters& p,
    const Controls& c,const NumericalSettings& n,SolveMode m,Residual& r) noexcept {
    Evaluation a;auto status=assemble(x,s,h,p,c,n,m,a);r=a.residual;return status;
}
Status evaluate_residual_and_jacobian(const StateVector& x,double s,const CommittedHistory& h,const PreparedParameters& p,
    const Controls& c,const NumericalSettings& n,SolveMode m,Residual& r,Jacobian& j) noexcept {
    Evaluation a;auto status=assemble(x,s,h,p,c,n,m,a);r=a.residual;j=a.jacobian;return status;
}
}
