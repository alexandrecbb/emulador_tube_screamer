#include "ts808/model.hpp"
#include <catch2/catch_test_macros.hpp>
#include <limits>
using namespace ts808;
TEST_CASE("DC hold and rejected steps preserve committed history") {
    Model model;REQUIRE(model.prepare({}, {}, {}).ok);REQUIRE(model.initialize_dc(0).status.ok);
    const StateVector dc=model.state();
    for(int i=0;i<100;++i)REQUIRE(model.advance(0).status.ok);
    for(int i=0;i<31;++i)REQUIRE(std::abs(model.state()[i]-dc[i])<(is_current(i)?1e-9:1e-6));
    const StateVector before=model.state();const auto history=model.history();
    auto step=model.advance(std::numeric_limits<double>::quiet_NaN());REQUIRE_FALSE(step.status.ok);
    REQUIRE((model.state()-before).isZero(0));
    for(int i=0;i<12;++i){REQUIRE(model.history().capacitors[i].voltage_V==history.capacitors[i].voltage_V);REQUIRE(model.history().capacitors[i].current_A==history.capacitors[i].current_A);}
    REQUIRE_FALSE(model.advance(0).status.ok);
    REQUIRE(model.prepare({}, {}, {}).ok);REQUIRE(model.initialize_dc(0).status.ok);REQUIRE(model.advance(0).status.ok);
}
TEST_CASE("Invalid controls and uninitialized operations return typed failures") {
    Model model;REQUIRE_FALSE(model.advance(0).status.ok);
    REQUIRE_FALSE(model.prepare({}, {-1,.5,.5}, {}).ok);
    REQUIRE(model.prepare({}, {}, {}).ok);REQUIRE_FALSE(model.advance(0).status.ok);
}
