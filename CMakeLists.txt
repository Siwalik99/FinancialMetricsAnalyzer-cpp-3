cmake_minimum_required(VERSION 3.16)
project(ConvertedApplication)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add executable
add_executable(ConvertedApp main.cpp)

# Add compiler flags
if(MSVC)
    target_compile_options(ConvertedApp PRIVATE /W4)
else()
    target_compile_options(ConvertedApp PRIVATE -Wall -Wextra -pedantic)
endif()

# Original source files: 8
# Generated from: FinancialMetricsAnalyzer/.streamlit/config.toml, FinancialMetricsAnalyzer/app.py, FinancialMetricsAnalyzer/components/calculator.py, FinancialMetricsAnalyzer/components/education.py, FinancialMetricsAnalyzer/components/simulator.py...
