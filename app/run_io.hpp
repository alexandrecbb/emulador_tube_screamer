#pragma once
#include "ts808/model.hpp"
#include <nlohmann/json.hpp>
#include <filesystem>
#include <ostream>
namespace ts808::offline {
using Json=nlohmann::json;
struct Case { Json document;Controls controls;NumericalSettings settings;std::uint64_t samples; };
Case read_case(const std::filesystem::path&);
double stimulus(const Json&,double);
void write_values(std::ostream&,std::span<const double>);
void write_row(std::ostream&,double,const StateVector&);
Json diagnostics(const NumericalDiagnostics&);
void write_json(const std::filesystem::path&,const Json&);
}
