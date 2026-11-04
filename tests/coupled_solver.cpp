#include "ts808/model.hpp"
#include "ts808/block_solve.hpp"
#include <catch2/catch_test_macros.hpp>
using namespace ts808;
TEST_CASE("Schur agrees with the diagnostic full solve at every control corner") {
    for(double d:{0.,.5,1.})for(double t:{0.,.5,1.})for(double v:{0.,.5,1.}){
        auto x=dc_initial_guess();Evaluation a;NumericalSettings s;
        REQUIRE(assemble(x,0,{}, {},{d,t,v},s,SolveMode::dc,a).ok);
        StateVector ds,df;auto status=block_solve(a.jacobian,-a.residual,s,ds);INFO("controls "<<d<<","<<t<<","<<v<<" reason "<<static_cast<int>(status.diagnostics.reason)<<" block "<<status.diagnostics.block<<" rcond "<<status.diagnostics.rcond.value);REQUIRE(status.ok);
        REQUIRE(full_solve(a.jacobian,-a.residual,s,df).ok);
        for(int i=0;i<31;++i)if(is_current(i)){ds[i]/=s.current_scale_A;df[i]/=s.current_scale_A;}
        REQUIRE((ds-df).lpNorm<Eigen::Infinity>()/std::max(1.,df.lpNorm<Eigen::Infinity>())<=1e-9);
    }
}
TEST_CASE("Singular blocks fail without fallback") {
    StateVector d;auto s=block_solve(Jacobian::Zero(),Residual::Ones(),{},d);
    REQUIRE_FALSE(s.ok);REQUIRE(s.diagnostics.reason==FailureReason::singular_internal);
    REQUIRE(s.diagnostics.block==0);
}
