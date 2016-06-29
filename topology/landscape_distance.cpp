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



#include <utility>
#include <fstream>
#include "hungarianC.h"
#include "persistenceBarcode.h"
#include "persistenceLandscape.h"
#include "landscape_distance.h"
#include <boost/python.hpp>

using namespace boost::python;

double Landscape::distance(object persist_1, object persist_2, object degree) {
  boost::python::list p1_list = extract<boost::python::list>(persist_1);
  boost::python::list p2_list = extract<boost::python::list>(persist_2);
  std::vector<std::pair<double,double>> p1;
  std::vector<std::pair<double,double>> p2;
  int p1_len = len(p1_list);
  int p2_len = len(p2_list);
  int deg = extract<int>(degree);
  for (int i=0; i < p1_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p1_list[i]);
    if (extract<int>(val[2]) == deg) {
      double start = extract<double>(val[0]);
      double end = extract<double>(val[1]);
      p1.push_back(std::make_pair(start, end));
    }
  }
  for (int i=0; i < p2_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p2_list[i]);
    if (extract<int>(val[2]) == deg) {
      double start = extract<double>(val[0]);
      double end = extract<double>(val[1]);
      p2.push_back(std::make_pair(start,end));
    }
  }
  PersistenceBarcodes b1(p1);
  PersistenceBarcodes b2(p2);
  PersistenceLandscape l1(b1);
  PersistenceLandscape l2(b2);
  return computeDiscanceOfLandscapes(l1,l2,2);
}
