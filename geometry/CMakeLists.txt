include_directories(${tstop_SOURCE_DIR}/geometry ${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})
file(GLOB geometry_sources ${tstop_SOURCE_DIR}/geometry/*.cpp ${tstop_SOURCE_DIR}/geometry/*.h)

add_library(geometry SHARED ${geometry_sources})
