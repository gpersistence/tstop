include_directories(${dynatopo_SOURCE_DIR}/geometry ${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})
file(GLOB geometry_sources ${dynatopo_SOURCE_DIR}/geometry/*.cpp ${dynatopo_SOURCE_DIR}/geometry/*.h)

add_library(geometry SHARED ${geometry_sources})
