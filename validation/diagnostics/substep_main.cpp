// Experimental convergence evidence only. This is deliberately not a model run
// accepted by the validation suite: the circuit integration rate is 768 kHz.
#include "run_io.hpp"
#include <fstream>
#include <iostream>

int main(int argc, char** argv) {
    using namespace ts808;
    using namespace ts808::offline;
    if (argc != 5 || std::string(argv[1]) != "--case" || std::string(argv[3]) != "--output") return 10;
    try {
        const Case c = read_case(argv[2]);
        if (c.document.at("analysis_kind") != "transient" ||
            (c.settings.rate_Hz != 192000 && c.settings.rate_Hz != 384000)) return 10;
        auto settings = c.settings;
        settings.rate_Hz = 768000;
        Model model;
        if (!model.prepare({}, c.controls, settings).ok || !model.initialize_dc(0).status.ok) return 20;
        const std::filesystem::path output = argv[4];
        if (!std::filesystem::create_directory(output)) return 50;
        Json metadata = {{"scope", "experimental substeps; not target-rate circuit acceptance"},
                         {"integration_rate_Hz", settings.rate_Hz},
                         {"output_rate_Hz", c.settings.rate_Hz},
                         {"substeps", settings.rate_Hz / c.settings.rate_Hz},
                         {"integrator", "trapezoidal"}, {"completion", "incomplete"},
                         {"physical_case_sha256", c.document.at("physical_case_sha256")}};
        write_json(output / "diagnostic.json", metadata);
        std::ofstream trace(output / "traces.f64le", std::ios::binary);
        write_row(trace, 0, model.state());
        const auto substeps = settings.rate_Hz / c.settings.rate_Hz;
        for (std::uint64_t sample = 1; sample < c.samples; ++sample) {
            for (std::uint32_t substep = 1; substep <= substeps; ++substep) {
                const auto index = (sample - 1) * substeps + substep;
                const double time = static_cast<double>(index) / settings.rate_Hz;
                if (!model.advance(stimulus(c.document.at("stimulus"), time)).status.ok) return 21;
            }
            write_row(trace, static_cast<double>(sample) / c.settings.rate_Hz, model.state());
        }
        trace.close();
        if (!trace) return 50;
        metadata["completion"] = "completed";
        metadata["sample_count"] = c.samples;
        write_json(output / "diagnostic.json", metadata);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 50;
    }
}
