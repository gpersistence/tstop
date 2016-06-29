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



#ifndef ZERO_PERSISTENCE_PYTHON_H
#define ZERO_PERSISTENCE_PYTHON_H 1
#include <iostream>
#include <boost/python.hpp>

#include "zero_persistence.h"
using namespace boost::python;

class ZeroDimensionPersistence {
  std::vector<FunctionValue> function_values;
 public:
  ZeroDimensionPersistence() { }
  ~ZeroDimensionPersistence() { function_values.clear(); }
  void add_function_value(boost::python::object index, boost::python::object time, boost::python::object value);
  boost::python::list sweep_persistence();
};
#endif /* ZERO_PERSISTENCE_PYTHON_H */
