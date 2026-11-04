#pragma once
#include <Eigen/Core>
#include <array>
#include <complex>
#include <cstdint>
#include <limits>

namespace ts808 {
using Scalar = double;
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559);
inline constexpr int unknown_count=31;
using StateVector = Eigen::Matrix<double,31,1>;
using Residual = StateVector;
using Jacobian = Eigen::Matrix<double,31,31>;
using ComplexResponse = std::complex<double>;
enum Node : int { input, input_cap, input_base, dry_send, clip_plus, clip_minus,
    gain_rc, drive_end, z_clip, i_drive, tone_in, tone_minus, tone_wiper, tone_rc,
    tone_out, volume_cap, volume_top, z_tone, i_tone_low, i_tone_high,
    i_volume_high, switch_common, output_base, output_emitter, output_cap,
    output, input_emitter, clip_out, wet_send, vref, i_volume_low,
    gnd=-1, v9=-2, generator=-3 };
inline constexpr std::array<const char*,31> unknown_names={"input","input_cap",
    "input_base","dry_send","clip_plus","clip_minus","gain_rc","drive_end",
    "z_clip","i_drive","tone_in","tone_minus","tone_wiper","tone_rc",
    "tone_out","volume_cap","volume_top","z_tone","i_tone_low","i_tone_high",
    "i_volume_high","switch_common","output_base","output_emitter","output_cap",
    "output","input_emitter","clip_out","wet_send","vref","i_volume_low"};
inline constexpr bool is_current(int i) noexcept {
    return i==i_drive || i==i_tone_low || i==i_tone_high || i==i_volume_high || i==i_volume_low;
}
inline constexpr bool is_state(int i) noexcept { return i==z_clip || i==z_tone; }
inline constexpr bool voltage_row(int i) noexcept { return is_current(i) || is_state(i); }
struct Controls { double drive=.5, tone=.5, volume=.5; };
struct CapacitorHistory { double voltage_V=0, current_A=0; };
struct CommittedHistory {
    std::array<CapacitorHistory,12> capacitors{};
    std::array<double,2> opamp_derivatives{};
    std::array<double,2> previous_z{};
};
enum class SolveMode { dc, transient };
enum class SolveStage { configuration, dc, transient, linear };
enum class FailureReason { none, invalid_configuration, not_prepared, not_initialized,
    nonfinite_trial, singular_internal, ill_conditioned_internal, singular_boundary,
    ill_conditioned_boundary, linear_backward_error, non_descent_direction,
    line_search_exhausted, newton_budget_exhausted, invalid_grid };
struct AvailableScalar { double value=0; bool available=false; };
struct NumericalDiagnostics {
    SolveStage stage=SolveStage::configuration;
    FailureReason reason=FailureReason::none;
    std::uint64_t failed_sample_index=0;
    std::uint32_t iterations=0, trials=0;
    int block=-1, row=-1, rank=0;
    AvailableScalar residual_norm{}, increment_norm{}, rcond{}, backward_error{};
};
struct Status { bool ok=true; NumericalDiagnostics diagnostics{}; };
struct DcResult { Status status; std::uint32_t iterations=0; };
struct StepResult {
    Status status;
    std::uint64_t committed_sample_index=0;
    double output_V=0;
    bool output_available=false;
};
struct NumericalSettings {
    enum class RowScaling { physical_only, max_abs_after_physical };
    RowScaling row_scaling=RowScaling::max_abs_after_physical;
    std::uint32_t rate_Hz=192000;
    double atol_current_A=1e-12, atol_voltage_V=1e-9, rtol_residual=1e-9;
    double atol_increment_current_A=1e-12, atol_increment_voltage_V=1e-9, rtol_increment=1e-9;
    std::uint32_t max_newton_dc=100, max_newton_transient=32, max_line_search=9;
    double armijo_c1=1e-4, voltage_scale_V=1, current_scale_A=1e-3;
    double pivot_epsilon_factor=64, minimum_rcond=1e-12;
    double maximum_backward_error=1e-10, maximum_schur_difference=1e-9;
    enum class DiagnosticMode { normal, checked } diagnostic_mode=DiagnosticMode::normal;
};
inline Status failure(FailureReason reason, SolveStage stage) noexcept {
    Status s; s.ok=false; s.diagnostics.reason=reason; s.diagnostics.stage=stage; return s;
}
}
