#include "ts808/stages.hpp"
#include <catch2/catch_test_macros.hpp>
#include <cmath>
using namespace ts808;
TEST_CASE("Diode and BJT derivatives agree with perturbations") {
    const PreparedParameters p;const double vt=thermal_voltage(p.temperature);
    for(double v:{-.2,0.,.1,.3,.6,.8}){
        const auto d=diode(v,p.diode,vt);const double h=1e-6;
        const double fd=(diode(v+h,p.diode,vt).current-diode(v-h,p.diode,vt).current)/(2*h);
        REQUIRE(std::abs(fd-d.conductance)<1e-10+1e-7*std::abs(d.conductance));
    }
    for(double vbe:{-.2,0.,.6,.7})for(double vbc:{-1.,-.2,0.,.5}){
        const auto q=bjt(vbe,vbc,p.bjt,vt);REQUIRE(std::abs(q.collector+q.base+q.emitter)<1e-17);
        for(int k=0;k<2;++k){const double h=1e-6;
            const auto a=bjt(vbe+(k==0?h:0),vbc+(k==1?h:0),p.bjt,vt);
            const auto b=bjt(vbe-(k==0?h:0),vbc-(k==1?h:0),p.bjt,vt);
            REQUIRE(std::abs((a.collector-b.collector)/(2*h)-q.dc[k])<1e-10+1e-7*std::abs(q.dc[k]));
            REQUIRE(std::abs((a.base-b.base)/(2*h)-q.db[k])<1e-10+1e-7*std::abs(q.db[k]));
        }
    }
}
TEST_CASE("Saturation is central identity with C2 joins and preserved headroom") {
    const OpampParameters p;const double l=4.5-p.headroom_plus-p.W_plus;
    for(double z:{-l,-1.,0.,1.,l}){const auto s=saturation(z,p,9);REQUIRE(s.value==z);REQUIRE(s.derivative==1);REQUIRE(s.second==0);}
    for(double sign:{-1.,1.})for(double offset:{-1e-7,0.,1e-7}){
        const auto s=saturation(sign*(l+offset),p,9);
        REQUIRE(std::abs(s.value-sign*(l+offset))<1e-12);
        REQUIRE(std::abs(s.derivative-1)<1e-10);REQUIRE(std::abs(s.second)<4e-6);
    }
    for(double z:{-10.,-4.,4.,10.}){
        const auto s=saturation(z,p,9);const double h=1e-5;
        REQUIRE(std::abs((saturation(z+h,p,9).value-saturation(z-h,p,9).value)/(2*h)-s.derivative)<1e-8);
        REQUIRE(std::abs(s.value)<=4.5-p.headroom_plus);REQUIRE(s.derivative>=0);
    }
}
TEST_CASE("Full assembly analytic Jacobian has neighboring finite difference agreement") {
    PreparedParameters p;Controls c;NumericalSettings settings;CommittedHistory hist;
    StateVector x=StateVector::Constant(4.4);x[input]=x[output]=x[tone_rc]=0;
    x[input_emitter]=x[output_emitter]=3.8;x[z_clip]=.2;x[z_tone]=-.1;
    for(int i=0;i<31;++i)if(is_current(i))x[i]=1e-6;
    hist.previous_z={.2,-.1};
    for(int k=0;k<12;++k){const auto& cap=p.capacitors[k];hist.capacitors[k].voltage_V=node_voltage(cap.a,x,.01,p)-node_voltage(cap.b,x,.01,p);}
    for(auto mode:{SolveMode::dc,SolveMode::transient}){
        Residual r;Jacobian j;REQUIRE(evaluate_residual_and_jacobian(x,.01,hist,p,c,settings,mode,r,j).ok);
        for(int col=0;col<31;++col){int passes=0;
            for(double step:{1e-3,1e-4,1e-5,1e-6,1e-7}){
                const double xs=is_current(col)?1e-3:1.;const double h=step*xs;
                StateVector xp=x,xm=x;xp[col]+=h;xm[col]-=h;Residual rp,rm;
                REQUIRE(evaluate_residual(xp,.01,hist,p,c,settings,mode,rp).ok);
                REQUIRE(evaluate_residual(xm,.01,hist,p,c,settings,mode,rm).ok);
                bool good=true;
                for(int row=0;row<31;++row){const double rs=voltage_row(row)?1:1e-3;
                    const double analytic=j(row,col)*xs/rs, fd=(rp[row]-rm[row])/(2*h)*xs/rs;
                    if(std::abs(analytic-fd)>1e-7+1e-5*std::abs(analytic)){good=false; if(step==1e-5)WARN("mode "<<static_cast<int>(mode)<<" row "<<row<<" col "<<col<<" analytic "<<analytic<<" finite "<<fd);}}
                passes=good?passes+1:0;if(passes>=2)break;
            }
            INFO("column "<<col);REQUIRE(passes>=2);
        }
    }
}
