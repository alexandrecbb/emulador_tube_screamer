#pragma once
#include "devices.hpp"
namespace ts808 {
struct Evaluation { Residual residual, contributions; Jacobian jacobian; };
Status assemble(const StateVector&, double source, const CommittedHistory&,
                const PreparedParameters&, const Controls&, const NumericalSettings&,
                SolveMode, Evaluation&) noexcept;
Status evaluate_residual(const StateVector&,double,const CommittedHistory&,
    const PreparedParameters&,const Controls&,const NumericalSettings&,SolveMode,Residual&) noexcept;
Status evaluate_residual_and_jacobian(const StateVector&,double,const CommittedHistory&,
    const PreparedParameters&,const Controls&,const NumericalSettings&,SolveMode,Residual&,Jacobian&) noexcept;
double node_voltage(int,const StateVector&,double,const PreparedParameters&) noexcept;
}
