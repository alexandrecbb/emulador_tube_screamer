#include "ts808/linear_response.hpp"
#include "ts808/model.hpp"
#include <catch2/catch_test_macros.hpp>
#include <numbers>
using namespace ts808;
TEST_CASE("Continuous and trapezoidal responses qualify all 27 loaded control triples") {
    for(double d:{0.,.5,1.})for(double t:{0.,.5,1.})for(double v:{0.,.5,1.}){
        Model model;Controls controls{d,t,v};NumericalSettings settings;
        REQUIRE(model.prepare({},controls,settings).ok);REQUIRE(model.initialize_dc(0).status.ok);
        std::array<double,301> frequencies;for(int k=0;k<=300;++k)frequencies[k]=20*std::pow(10.,k/100.);
        std::array<ComplexResponse,301> continuous,discrete;
        REQUIRE(linear_response({},controls,model.state(),settings,frequencies,continuous,discrete).ok);
        // Bilinear recurrence at f equals the continuous descriptor at tan-warped f.
        std::array<double,1> warped{settings.rate_Hz/std::numbers::pi*std::tan(std::numbers::pi*1000/settings.rate_Hz)};
        std::array<double,1> physical{1000};std::array<ComplexResponse,1> ca,da,cb,db;
        REQUIRE(linear_response({},controls,model.state(),settings,physical,ca,da).ok);
        REQUIRE(linear_response({},controls,model.state(),settings,warped,cb,db).ok);
        REQUIRE(std::abs(da[0]-cb[0])<1e-9*std::max(1.,std::abs(cb[0])));
    }
}
