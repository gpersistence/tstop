//TSTOP
//
//This program is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//This program is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with this program.  If not, see <http://www.gnu.org/licenses/>.



/**
 * rips_python.cpp 
 *
 * Interface between the python time series functionality and 
 * the sparse and full rips filtration in C++
 *
 * Dec 4 2015 Shelby Davis davis@brsc.com
 * Govt POC: Lee Seversky AFRL / RISA Lee.Seversky@us.af.mil
 */

#include <limits>
#include <boost/python.hpp>
#include "filtration.h"
#include "generalized_metric_space.h"
#include "rips_python.hpp"

using namespace boost::python;


/* points is a list of lists of floats, corresponding to the 'windows' field in a Segment in python */
RipsFiltration* RIPS_python::rips_filtration_generator(boost::python::object points, 
						       boost::python::object max_d) 
{
  int _max_d = extract<int>(max_d);
  boost::python::list points_list = extract<boost::python::list>(points);
  int points_len = len(points_list);
  Points c_points;
  for (int i = 0; i < points_len; ++i) {
    c_points.push_back(Vector(points_list[i]));
  }

  RipsFiltration *result = new RipsFiltration(c_points, _max_d);

  return result;
}

SparseRipsFiltration* RIPS_python::sparse_rips_filtration_generator(boost::python::object points, 
								    boost::python::object max_simplices, 
								    boost::python::object epsilon,
								    boost::python::object max_d) 
{
  int _max_d = extract<int>(max_d);
  boost::python::list points_list = extract<boost::python::list>(points);
  int points_len = len(points_list);
  Points c_points;
  for (int i = 0; i < points_len; ++i) {
    c_points.push_back(Vector(points_list[i]));
  }

  SparseRipsFiltration *result = NULL;
  if (!max_simplices.is_none()) {
    result = new SparseRipsFiltration(c_points, _max_d);
    result->set_max_simplices(extract<int>(max_simplices));
  } else if (!epsilon.is_none()) {
    result = new SparseRipsFiltration(c_points, _max_d, extract<double>(epsilon));
  } else {
    result = new SparseRipsFiltration(c_points, _max_d);
  }

  return result;
}
