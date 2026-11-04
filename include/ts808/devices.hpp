#pragma once
#include "parameters.hpp"
namespace ts808 {
struct CurrentLaw { double current, conductance; };
struct BjtLaw {
    double collector, base, emitter;
    // Derivatives with respect to VBE and VBC, respectively.
    std::array<double,2> dc, db, de;
};
struct Saturation { double value, derivative, second; };
struct StateLaw { double value, de, dz, drive; };
CurrentLaw diode(double voltage, const DiodeParameters&, double vt) noexcept;
BjtLaw bjt(double vbe, double vbc, const BjtParameters&, double vt) noexcept;
Saturation saturation(double z, const OpampParameters&, double supply) noexcept;
StateLaw opamp_state(double e, double z, const OpampParameters&, double supply) noexcept;
}
