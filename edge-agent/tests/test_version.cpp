#include <gtest/gtest.h>

#include <algorithm>

#include "edge_agent/version.hpp"

TEST(Version, IsNotEmpty) { EXPECT_FALSE(edge_agent::version().empty()); }

TEST(Version, HasThreeParts) {
    const auto v = edge_agent::version();
    EXPECT_EQ(std::count(v.begin(), v.end(), '.'), 2);
}
