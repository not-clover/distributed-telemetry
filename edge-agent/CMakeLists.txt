cmake_minimum_required(VERSION 3.20)

project(cellpulse_edge_agent
  VERSION 0.1.0
  DESCRIPTION "C++ edge agent for CellPulse"
  LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)  # lets VS Code / clangd understand the project

option(EDGE_AGENT_BUILD_TESTS "Build the unit tests" ON)
option(EDGE_AGENT_WERROR "Treat compiler warnings as errors (used in CI)" OFF)

# Compiler warnings for everything we build
add_library(edge_agent_warnings INTERFACE)
if(MSVC)
  target_compile_options(edge_agent_warnings INTERFACE /W4 /permissive-)
  if(EDGE_AGENT_WERROR)
    target_compile_options(edge_agent_warnings INTERFACE /WX)
  endif()
else()
  target_compile_options(edge_agent_warnings INTERFACE -Wall -Wextra -Wpedantic -Wshadow -Wconversion)
  if(EDGE_AGENT_WERROR)
    target_compile_options(edge_agent_warnings INTERFACE -Werror)
  endif()
endif()

# Core library: all the real logic goes here, so it can be unit-tested.
# Add new source files to this list as you create them.
add_library(edge_agent_core
  src/version.cpp
)
target_include_directories(edge_agent_core PUBLIC include)
target_compile_definitions(edge_agent_core PRIVATE EDGE_AGENT_VERSION="${PROJECT_VERSION}")
target_link_libraries(edge_agent_core PRIVATE edge_agent_warnings)

# Executable: a thin main() on top of the core library
add_executable(edge-agent src/main.cpp)
target_link_libraries(edge-agent PRIVATE edge_agent_core edge_agent_warnings)

# Tests (GoogleTest is downloaded automatically the first time you configure)
if(EDGE_AGENT_BUILD_TESTS)
  include(FetchContent)
  FetchContent_Declare(googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.15.2.zip
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
  set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)  # needed on Windows/MSVC
  set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(googletest)

  enable_testing()
  add_executable(edge_agent_tests
    tests/test_version.cpp
  )
  target_link_libraries(edge_agent_tests PRIVATE edge_agent_core edge_agent_warnings GTest::gtest_main)
  include(GoogleTest)
  gtest_discover_tests(edge_agent_tests)
endif()
