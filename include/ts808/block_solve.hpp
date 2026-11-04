#pragma once
#include "types.hpp"
namespace ts808 {
Status block_solve(const Jacobian&,const Residual& rhs,const NumericalSettings&,StateVector&) noexcept;
Status full_solve(const Jacobian&,const Residual& rhs,const NumericalSettings&,StateVector&) noexcept;
}
