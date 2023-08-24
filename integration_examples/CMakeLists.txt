# Project settings
set(PROJECT_NAME main)
project(${PROJECT_NAME})

# Basic settings
cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Directory variables
set(RESOURCE_DIR resources)
set(RESOURCE_DIR_INC .)
set(SRC_DIR src)
#set(BUILD_DIR build)

# Output directory settings
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/)

# Tools
set(NRES .scripts/nr_gen_aio.py)

# Python commandline
if(WIN32) #Windows does not use the `python3` binary name for Python
	set(PYTHON_BIN python)
else()
	set(PYTHON_BIN python3)
endif()

# Pre-build scripts
execute_process(COMMAND ${PYTHON_BIN} ${NRES} -d ${RESOURCE_DIR})

# Includes
include_directories(${RESOURCE_DIR_INC})

# Executable settings
add_executable(${PROJECT_NAME} ${SRC_DIR}/main.cpp)

# Compiler options
target_compile_options(${PROJECT_NAME} PRIVATE
	$<$<CXX_COMPILER_ID:MSVC>:/W4>
	$<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion>
)
