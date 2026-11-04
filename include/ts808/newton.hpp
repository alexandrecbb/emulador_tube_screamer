#pragma once
#include "stages.hpp"
namespace ts808 {
Status newton(StateVector&,double,const CommittedHistory&,const PreparedParameters&,
    const Controls&,const NumericalSettings&,SolveMode) noexcept;
StateVector dc_initial_guess() noexcept;
}
