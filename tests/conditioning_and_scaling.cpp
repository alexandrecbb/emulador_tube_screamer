#include "ts808/block_solve.hpp"
#include "ts808/newton.hpp"
#include <catch2/catch_test_macros.hpp>
using namespace ts808;
TEST_CASE("Approved row equilibration fixes the measured clipping scale failure") {
    NumericalSettings s;Evaluation e;auto x=dc_initial_guess();
    REQUIRE(assemble(x,0,{}, {},{},s,SolveMode::dc,e).ok);StateVector delta;
    s.row_scaling=NumericalSettings::RowScaling::physical_only;
    auto status=block_solve(e.jacobian,-e.residual,s,delta);
    REQUIRE_FALSE(status.ok);REQUIRE(status.diagnostics.reason==FailureReason::ill_conditioned_internal);
    REQUIRE(status.diagnostics.block==1);REQUIRE(status.diagnostics.rcond.value<1e-12);
    s.row_scaling=NumericalSettings::RowScaling::max_abs_after_physical;
    status=block_solve(e.jacobian,-e.residual,s,delta);REQUIRE(status.ok);
    REQUIRE(status.diagnostics.backward_error.available);REQUIRE(status.diagnostics.backward_error.value<=1e-10);
}

TEST_CASE("Rank and reciprocal condition failures remain visible after equilibration") {
    NumericalSettings s;StateVector solution;
    auto fixture=[](double epsilon){
        Jacobian j=Jacobian::Zero();
        for(int i=0;i<31;++i)j(i,i)=(voltage_row(i)?1:.001)/(is_current(i)?.001:1);
        j(0,1)=.001;j(1,0)=.001;j(1,1)=.001*(1+epsilon);
        return j;
    };
    auto status=block_solve(fixture(0),Residual::Ones(),s,solution);
    REQUIRE_FALSE(status.ok);REQUIRE(status.diagnostics.reason==FailureReason::singular_internal);
    status=block_solve(fixture(1e-12),Residual::Ones(),s,solution);
    REQUIRE_FALSE(status.ok);REQUIRE(status.diagnostics.reason==FailureReason::ill_conditioned_internal);
    status=block_solve(fixture(1e-9),Residual::Ones(),s,solution);
    REQUIRE(status.ok);
}
