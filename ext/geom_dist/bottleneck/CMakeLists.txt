project(geom_bottleneck)
cmake_minimum_required(VERSION 2.8.9)
include (GenerateExportHeader)

# Default to Release
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose the type of build, options are: Debug Release RelWithDebInfo MinSizeRel." FORCE)
endif(NOT CMAKE_BUILD_TYPE)

# Add path to ANN header files
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/include/ANN")

set(CXX_FLAGS ${CMAKE_CXX_FLAGS_RELEASE})

if(NOT WIN32)
    set(CMAKE_CXX_FLAGS "-O3 -DNDEBUG -DBOOST_DISABLE_ASSERTS")
    add_definitions(-std=c++11 -fPIC)
endif(NOT WIN32)

file(GLOB ANN_SRC_FILES src/ann/*.cpp)

add_library(bottleneck src/bottleneck.cpp src/bound_match.cpp src/neighb_oracle.cpp src/basic_defs.cpp ${ANN_SRC_FILES})
if (WIN32)
    GENERATE_EXPORT_HEADER(bottleneck
               BASE_NAME bottleneck
               EXPORT_MACRO_NAME bottleneck_EXPORT
               EXPORT_FILE_NAME bottleneck_export.h
               STATIC_DEFINE bottleneck_BUILT_AS_STATIC)
endif(WIN32)
