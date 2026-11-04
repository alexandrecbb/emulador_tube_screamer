#include "ts808/devices.hpp"
#include <cmath>
#include <numbers>
namespace ts808 {
CurrentLaw diode(double v, const DiodeParameters& p, double vt) noexcept {
    const double a=v/(p.n*vt), ex=std::exp(a);
    return {p.Is*std::expm1(a),p.Is*ex/(p.n*vt)};
}
BjtLaw bjt(double vbe, double vbc, const BjtParameters& p, double vt) noexcept {
    const double af=p.BF/(p.BF+1), ar=p.BR/(p.BR+1);
    const double f=p.Is/af*std::expm1(vbe/(p.NF*vt));
    const double r=p.Is/ar*std::expm1(vbc/(p.NR*vt));
    const double df=p.Is/af*std::exp(vbe/(p.NF*vt))/(p.NF*vt);
    const double dr=p.Is/ar*std::exp(vbc/(p.NR*vt))/(p.NR*vt);
    return {af*f-r,(1-af)*f+(1-ar)*r,-f+ar*r,
        {af*df,-dr},{(1-af)*df,(1-ar)*dr},{-df,ar*dr}};
}
Saturation saturation(double z, const OpampParameters& p, double supply) noexcept {
    const double sign=z<0?-1:1, w=sign<0?p.W_minus:p.W_plus;
    const double h=supply/2-(sign<0?p.headroom_minus:p.headroom_plus), l=h-w;
    if (std::abs(z)<=l) return {z,1,0};
    const double s=(std::abs(z)-l)/w, q=std::tanh(s), ex=std::exp(-2*s);
    const double d=4*ex/((1+ex)*(1+ex));
    return {sign*(l+w*q),d,-sign*2*q*d/w};
}
StateLaw opamp_state(double e,double z,const OpampParameters& p,double supply) noexcept {
    const auto sat=saturation(z,p,supply);
    const double omega=2*std::numbers::pi*p.GBW/p.A0;
    const double drive=omega*(p.A0*e-z)-(z-sat.value)/p.tau;
    const double q=std::tanh(drive/p.SR), ex=std::exp(-2*std::abs(drive/p.SR));
    const double d=4*ex/((1+ex)*(1+ex));
    return {p.SR*q,d*omega*p.A0,d*(-omega-(1-sat.derivative)/p.tau),drive};
}
}
