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



#ifndef LANDSCAPE_DISTANCE_H
#define LANDSCAPE_DISTANCE_H 1
#include <boost/python.hpp>
namespace Landscape {
  double distance(boost::python::object persistence_1, 
		  boost::python::object persistence_2,
		  boost::python::object degree);
}

#endif
