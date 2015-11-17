cmake_minimum_required(VERSION 2.8)

enable_language (Fortran)
enable_testing ()

set(CLAW_C ${CMAKE_SOURCE_DIR}/../claw_c.py)

# List of test directories
add_subdirectory(loop)
