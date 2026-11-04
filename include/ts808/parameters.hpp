#pragma once
#include "types.hpp"
#include <array>

namespace ts808 {
struct Passive { const char* id; int a,b; double value; };
struct DiodeParameters { double Is=3.0193620074088285e-9, n=1.94; };
struct BjtParameters {
    double Is=1.1792496052020765e-14, BF=271.5505716517182,
        BR=4.2141277418153207, NF=.99569, NR=1;
};
struct OpampParameters {
    double A0=1e5, GBW=3e6, SR=1e6, Rid=5e6, bias_plus=25e-9,
        bias_minus=25e-9, offset=0, Ro=10000./51, headroom_plus=37./51,
        headroom_minus=37./51, W_plus=.25, W_minus=.25, tau=10e-6;
};
// Full immutable value copy is owned by Model after prepare; no JSON in core.
struct PreparedParameters {
    double supply=9, temperature=298.15;
    DiodeParameters diode{}; BjtParameters bjt{}; OpampParameters opamp{};
    std::array<Passive,22> resistors{{
        {"R_source",generator,input,1000},{"R_input",input_cap,input_base,1000},
        {"R_input_bias",input_base,vref,510000},{"R_input_emitter",input_emitter,gnd,10000},
        {"R_clip_bias",clip_plus,vref,10000},{"R_gain_lower",vref,gain_rc,4700},
        {"R_feedback",clip_minus,drive_end,51000},{"R_tone_input",clip_out,tone_in,1000},
        {"R_tone_bias",tone_in,vref,10000},{"R_tone_feedback",tone_minus,tone_out,1000},
        {"R_tone_shelf",tone_rc,gnd,220},{"R_volume_input",volume_cap,volume_top,1000},
        {"R_dry_bias",dry_send,vref,510000},{"R_switch_common_bias",switch_common,vref,510000},
        {"R_output_bias",output_base,vref,510000},{"R_output_emitter",output_emitter,gnd,10000},
        {"R_output_series",output_emitter,output_cap,100},{"R_output_shunt",output,gnd,10000},
        {"R_load",output,gnd,1e6},{"R_bias_upper",v9,vref,10000},
        {"R_bias_lower",vref,gnd,10000},{"J_wet",wet_send,switch_common,383.29731360711594}
    }};
    std::array<Passive,12> capacitors{{
        {"C_input",input,input_cap,20e-9},{"C_clip_input",input_emitter,clip_plus,1e-6},
        {"C_gain_lower",gain_rc,clip_minus,47e-9},{"C_feedback",clip_minus,clip_out,51e-12},
        {"C_tone_lowpass",tone_in,gnd,220e-9},{"C_tone_shelf",tone_wiper,tone_rc,220e-9},
        {"C_volume_input",tone_out,volume_cap,1e-6},{"C_dry",input_emitter,dry_send,100e-9},
        {"C_output_input",switch_common,output_base,100e-9},{"C_output",output_cap,output,10e-6},
        {"C_bias",vref,gnd,47e-6},{"C_supply",v9,gnd,100e-6}
    }};
    double drive_total=500000, tone_total=20000, volume_total=100000;
};
inline constexpr double thermal_voltage(double temperature) noexcept {
    return 1.380649e-23*temperature/1.602176634e-19;
}
}
