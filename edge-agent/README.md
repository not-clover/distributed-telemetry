# Edge agent (C++)

Owner: @AnvikaVihaan

A C++ agent that simulates 5G cells and streams their KPIs to the CellPulse collectors,
using the same protocol as the Python agent (`proto/cellpulse/v1/telemetry.proto`).

<!-- TODO(@AnvikaVihaan): describe the design, data structures and status in your own words. -->

## Build and test

Requires CMake ≥ 3.20 and a C++20 compiler (GCC 11+, Clang 14+ or Visual Studio 2022).

```bash
cd edge-agent
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
./build/edge-agent        # Windows (Visual Studio): build\Debug\edge-agent.exe
```

## Layout

| Path | What goes there |
|------|-----------------|
| `include/edge_agent/` | Public headers (`.hpp`) |
| `src/` | Implementation (`.cpp`) and `main.cpp` |
| `tests/` | GoogleTest unit tests, one file per component |

When you add a new component: create the header in `include/edge_agent/`, the source in `src/`,
a test in `tests/`, and add both `.cpp` files to `CMakeLists.txt`.
