#pragma once
#include "newton.hpp"
namespace ts808 {
class Model {
    PreparedParameters parameters_{};Controls controls_{};NumericalSettings settings_{};
    StateVector state_=StateVector::Zero();CommittedHistory history_{};
    NumericalDiagnostics diagnostics_{};std::uint64_t index_=0;
    bool prepared_=false, initialized_=false, failed_=false;
public:
    Status prepare(const PreparedParameters&,const Controls&,const NumericalSettings&) noexcept;
    DcResult initialize_dc(double generator_voltage) noexcept;
    StepResult advance(double next_generator_voltage) noexcept;
    const StateVector& state() const noexcept {return state_;}
    const CommittedHistory& history() const noexcept {return history_;}
    const NumericalDiagnostics& diagnostics() const noexcept {return diagnostics_;}
};
}
