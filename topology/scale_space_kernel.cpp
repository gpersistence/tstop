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



#include <memory>
#include <cmath>
#include <boost/python.hpp>
#include "scale_space_kernel.h"

double ScaleSpaceKernel::similarity(boost::python::object list_1, 
				    boost::python::object list_2,
				    double sigma) 
{
  int list_len_1 = boost::python::len(list_1);
  int list_len_2 = boost::python::len(list_2);
  if (list_len_1 <= 1 || list_len_2 <= 1) 
  {
    return 0.0;
  }
  boost::python::list _list_1 = boost::python::extract<boost::python::list>(list_1);
  boost::python::list _list_2 = boost::python::extract<boost::python::list>(list_2);

  std::unique_ptr<double[]> l1(new double[list_len_1*2]);
  for (int i=0; i < list_len_1; i++) 
  {
    boost::python::tuple _l1 = boost::python::extract<boost::python::tuple>(_list_1[i]);
    l1[i*2 + 0] = boost::python::extract<double>(_l1[0]);
    l1[i*2 + 1] = boost::python::extract<double>(_l1[1]);
  }
  std::unique_ptr<double[]> l2(new double[list_len_2*2]);
  for (int j=0; j < list_len_2; j++) 
  {
    boost::python::tuple _l2 = boost::python::extract<boost::python::tuple>(_list_2[j]);
    l2[j*2 + 0] = boost::python::extract<double>(_l2[0]);
    l2[j*2 + 1] = boost::python::extract<double>(_l2[1]);
  }
  double scale = -1.0 / sigma / 8.0;
  double accum = 0.0;
  for (int i=0; i < list_len_1; i++) 
  {
    double l1_x = l1[i*2+0];
    double l1_y = l1[i*2+1];
    for (int j=0; j < list_len_2; j++) 
    {
      double l2_x = l2[j*2+0];
      double l2_y = l2[j*2+1];
      double xx = l1_x - l2_x;
      double yy = l1_y - l2_y;
      double xy = l1_x - l2_y;
      double yx = l1_y - l2_x;
      accum += 
	std::exp((xx * xx + yy * yy) * scale) - 
	std::exp((xy * xy + yx * yx) * scale);
    }
  }
  return accum / (8.0 * sigma * M_PI);
}
