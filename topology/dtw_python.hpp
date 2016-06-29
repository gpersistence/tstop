#ifndef DTW_PYTHON_H
#define DTW_PYTHON_H 1

#include <boost/python.hpp>

namespace DTW_python {
  /* nearest_neigbor returns a list of tuples (index, distance) of the
   * nearest neighbot in the training set for each element in the test
   * set. */
  boost::python::list nearest_neighbor(boost::python::object time_series_train, 
				       boost::python::object time_series_test); 
  /* distance returns the DTW distance between two segments*/
  double distance(boost::python::object segment_a, 
		  boost::python::object segment_b); 
};

#endif
