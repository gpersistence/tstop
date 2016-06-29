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
 * zero_persistence_python.cpp
 * 
 * Interface between python code and the code for calculating zero dimensional persistence diagrams
 *
 * April 22 2016 Shelby davis davis@brsc.com
 * Govt POC: Lee Seversky AFRL / RISA Lee.Seversky@us.af.mil
 */

#include "zero_persistence_python.h"

using namespace boost::python;

void ZeroDimensionPersistence::add_function_value(boost::python::object index, 
						  boost::python::object time, 
						  boost::python::object value) {
  //  std::cout << "Adding point " << extract<int>(index) << " time " << extract<double>(time) << " value " << extract<double>(value) << std::endl;
  this->function_values.push_back(FunctionValue(extract<int>(index), extract<double>(time), extract<double>(value)));
}

boost::python::list ZeroDimensionPersistence::sweep_persistence() {
  ZeroPersistence p = ZeroPersistence(this->function_values);
  p.sweep_persistence();
  std::vector<std::pair<double,double> > zero_pd;
  p.get_root()->compute_all_pairs(zero_pd);
  boost::python::list pairs;
  for (std::vector<std::pair<double,double> >::iterator it = zero_pd.begin(); it != zero_pd.end(); ++it) {
    pairs.append(boost::python::make_tuple((*it).first, (*it).second));
  }
  return pairs;
}
