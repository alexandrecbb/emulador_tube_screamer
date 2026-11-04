#pragma once
#include "parameters.hpp"
#include <span>
namespace ts808 {
Status linear_response(const PreparedParameters&,const Controls&,const StateVector&,
    const NumericalSettings&,std::span<const double>,std::span<ComplexResponse>,std::span<ComplexResponse>) noexcept;
}
