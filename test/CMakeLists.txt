cmake_minimum_required(VERSION 2.8)

project(claw_c_test)

enable_language (Fortran)
enable_testing ()

set(CLAW_C ${CMAKE_SOURCE_DIR}/../claw_c.py)
set(CLAW_C_V2 ${CMAKE_SOURCE_DIR}/../claw_c_v2.py)

# List of test directories
add_subdirectory(loop)
