#pragma once

#include <string_view>

namespace edge_agent {

// Semantic version of the edge agent, set from CMakeLists.txt.
std::string_view version() noexcept;

}  // namespace edge_agent
