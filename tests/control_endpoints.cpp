#include "ts808/model.hpp"
#include <catch2/catch_test_macros.hpp>
#include <cmath>
using namespace ts808;
TEST_CASE("All 27 loaded DC control triples solve with exact endpoints") {
    for(double d:{0.,.5,1.})for(double t:{0.,.5,1.})for(double v:{0.,.5,1.}){
        INFO("controls "<<d<<","<<t<<","<<v);
        Model model;REQUIRE(model.prepare({}, {d,t,v}, {}).ok);
        auto dc=model.initialize_dc(0);INFO("DC reason "<<static_cast<int>(dc.status.diagnostics.reason)<<" block "<<dc.status.diagnostics.block<<" rcond "<<dc.status.diagnostics.rcond.value);REQUIRE(dc.status.ok);
        const auto& x=model.state();
        REQUIRE(x[vref]>4);REQUIRE(x[vref]<5);
        if(d==0)REQUIRE(std::abs(x[drive_end]-x[clip_out])<1e-9);
        if(t==0)REQUIRE(std::abs(x[tone_in]-x[tone_wiper])<1e-9);
        if(t==1)REQUIRE(std::abs(x[tone_wiper]-x[tone_minus])<1e-9);
        if(v==0)REQUIRE(std::abs(x[vref]-x[wet_send])<1e-9);
        if(v==1)REQUIRE(std::abs(x[wet_send]-x[volume_top])<1e-9);
        for(int i=0;i<20;++i){auto step=model.advance(0);INFO("step reason "<<static_cast<int>(step.status.diagnostics.reason));REQUIRE(step.status.ok);}
    }
}

TEST_CASE("All 27 control triples advance a raised cosine tone onset at both target rates") {
    for(auto rate:{192000u,384000u})for(double d:{0.,.5,1.})for(double t:{0.,.5,1.})for(double v:{0.,.5,1.}){
        NumericalSettings settings;settings.rate_Hz=rate;Model model;
        REQUIRE(model.prepare({}, {d,t,v}, settings).ok);REQUIRE(model.initialize_dc(0).status.ok);
        for(int sample=1;sample<=512;++sample){
            const double time=static_cast<double>(sample)/rate;
            const double envelope=.5*(1-std::cos(3.14159265358979323846*time/.005));
            const auto step=model.advance(.1*envelope*std::sin(2*3.14159265358979323846*1000*time));
            INFO("rate "<<rate<<" controls "<<d<<","<<t<<","<<v<<" sample "<<sample<<" reason "<<static_cast<int>(step.status.diagnostics.reason));
            REQUIRE(step.status.ok);REQUIRE(model.state().allFinite());
        }
    }
}
