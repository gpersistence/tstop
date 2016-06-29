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
 * dtw_python.cpp 
 *
 * Interface between the python time series functionality and the
 * dynamic time warping nearest neighbor functions in dtw.h from
 * Daniel Lemire at https://github.com/lemire/lbimproved
 *
 * Nov 1 2015 Shelby Davis davis@brsc.com
 * Govt POC: Lee Seversky AFRL / RISA Lee.Seversky@us.af.mil
 */

#include <limits>
#include <boost/python.hpp>
#include "dtw.h"
#include "dtw_python.hpp"

using namespace boost::python;

boost::python::list DTW_python::nearest_neighbor(boost::python::object time_series_train, 
					  boost::python::object time_series_test) 
{
  boost::python::list ts_train_list = extract<boost::python::list>(time_series_train);
  boost::python::list ts_test_list = extract<boost::python::list>(time_series_test);
  std::vector<std::vector<double>> train_sets;
  int train_len = len(ts_train_list);
  for (int i = 0; i < train_len; ++i) {
    boost::python::list train_element_py = extract<boost::python::list>(ts_train_list[i]);
    std::vector<double> train_element;
    int train_element_len = len(train_element_py);
    for (int j=0; j < train_element_len; ++j) {
      train_element.push_back(extract<double>(train_element_py[j]));
    }
    train_sets.push_back(train_element);
  }

  boost::python::list result;
  int test_len = len(ts_test_list);
  for (int i=0; i < test_len; ++i) {
    boost::python::list test_element_py = extract<boost::python::list>(ts_test_list[i]);
    std::vector<double> test_element;
    int test_element_len = len(test_element_py);
    for (int j=0; j < test_element_len; ++j) {
      test_element.push_back(extract<double>(test_element_py[j]));
    }
    LB_Improved nn(test_element, test_element_len / 10.0); // Arbitrarily set the window at 10%
    int match = -1;
    double best_distance = nn.getLowestCost();
    for (int j=0; j < train_len; ++j) {
      double new_distance = nn.test(train_sets[j]);
      if (new_distance < best_distance) {
	best_distance = new_distance;
	match = j;
      }
    }
    result.append(boost::python::make_tuple(match, best_distance));
  }
  return result;
}

double DTW_python::distance(boost::python::object segment_a, 
			    boost::python::object segment_b) 
{
  boost::python::list segment_a_py = extract<boost::python::list>(segment_a);
  std::vector<double> segment_a_element;
  int segment_a_len = len(segment_a_py);
  for (int j=0; j < segment_a_len; ++j) {
    segment_a_element.push_back(extract<double>(segment_a_py[j]));
  }

  boost::python::list segment_b_py = extract<boost::python::list>(segment_b);
  std::vector<double> segment_b_element;
  int segment_b_len = len(segment_b_py);
  for (int j=0; j < segment_b_len; ++j) {
    segment_b_element.push_back(extract<double>(segment_b_py[j]));
  }

  LB_Improved nn(segment_a_element, segment_a_len / 10.0); // Arbitrarily set the window at 10%

  double distance = nn.test(segment_b_element);
  return distance;
}
