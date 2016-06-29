#ifndef RIPS_PYTHON_H
#define RIPS_PYTHON_H 1

#include "topology/rips_filtration.h"
#include "topology/sparse_rips_filtration.h"
#include <boost/python.hpp>

namespace RIPS_python {
  SparseRipsFiltration *sparse_rips_filtration_generator(boost::python::object points,
							 boost::python::object max_simplices,
							 boost::python::object epsilon,
							 boost::python::object max_d); 
  RipsFiltration *rips_filtration_generator(boost::python::object points,
					    boost::python::object max_d); 
};

#endif
