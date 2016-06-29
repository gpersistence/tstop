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
#include "bottleneck_distance.h"
#include "persistence_diagram.h"

using namespace boost::python;

boost::python::list BottleneckDistance::match_points(object persist_1, 
						     object persist_2,
						     object degree) 
{
  boost::python::list p1_list = extract<boost::python::list>(persist_1);
  boost::python::list p2_list = extract<boost::python::list>(persist_2);
  std::vector<PersistentPair> p1;
  std::vector<PersistentPair> p2;
  int p1_len = len(p1_list);
  int p2_len = len(p2_list);
  int deg = extract<int>(degree);
  for (int i=0; i < p1_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p1_list[i]);
    if (extract<int>(val[2]) == deg) {
      p1.push_back(PersistentPair(extract<int>(val[2]),
				  extract<double>(val[0]),
				  extract<double>(val[1])));
    }
  }
  for (int i=0; i < p2_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p2_list[i]);
    if (extract<int>(val[2]) == deg) {
      p2.push_back(PersistentPair(extract<int>(val[2]),
				  extract<double>(val[0]),
				  extract<double>(val[1])));
    }
  }


  PersistenceDiagram persistence_1 = PersistenceDiagram(p1);
  PersistenceDiagram persistence_2 = PersistenceDiagram(p2);
  std::pair<std::vector<int>, std::vector<int>> matching = persistence_1.wasserstein_matching(persistence_2,1);
  boost::python::list result;

  std::vector<int> matching_a = matching.first;
  int a_index = 0;
  for (std::vector<int>::iterator it = matching_a.begin(); it != matching_a.end(); ++it, ++a_index) {
    if (*it == -1) {
      // Matched to the diagonal
      result.append(boost::python::make_tuple(boost::python::make_tuple(p1[a_index].birth, p1[a_index].death), 
			  boost::python::make_tuple((p1[a_index].birth+p1[a_index].death)/2.0, 
						    (p1[a_index].birth+p1[a_index].death)/2.0),
			  p1[a_index].l_inf_diagonal()));
    } else {
      result.append(boost::python::make_tuple(boost::python::make_tuple(p1[a_index].birth, p1[a_index].death), 
			  boost::python::make_tuple(p2[*it].birth, p2[*it].death),
			  p1[a_index].l_inf_norm(p2[*it])));
      
    }
  }
  std::vector<int> matching_b = matching.second;
  int b_index = 0;
  for (std::vector<int>::iterator it = matching_b.begin(); it != matching_b.end(); ++it, ++b_index) {
    if (*it == -1) {
      // Matched to the diagonal
      result.append(boost::python::make_tuple(boost::python::make_tuple(p2[b_index].birth, p2[b_index].death), 
					      boost::python::make_tuple((p2[b_index].birth+p2[b_index].death)/2.0, 
									(p2[b_index].birth+p2[b_index].death)/2.0),
			  p2[b_index].l_inf_diagonal()));
    } 
  }

  p1.clear();
  p2.clear();
  matching_a.clear();
  matching_b.clear();

  return result;
}
#include "bottleneck.h"
double BottleneckDistance::bottleneck_distance(object persist_1, 
					       object persist_2,
					       object degree) 
{
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
      p1.push_back(std::pair<double,double>( extract<double>(val[0]), extract<double>(val[1])));
    }
  }
  for (int i=0; i < p2_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p2_list[i]);
    if (extract<int>(val[2]) == deg) {
      p2.push_back(std::pair<double,double>( extract<double>(val[0]), extract<double>(val[1])));
    }
  }

  if (p1.size() != 0 and p2.size() != 0) {
    return geom_bt::bottleneckDistApproxInterval(p1, p2, 0.01 /* relative error, 1% */).first;
  } else {
    return -1.0;
  }
}
#include "wasserstein.h"
double BottleneckDistance::wasserstein_distance(object persist_1, 
						object persist_2,
						object degree,
						object power) 
{
  boost::python::list p1_list = extract<boost::python::list>(persist_1);
  boost::python::list p2_list = extract<boost::python::list>(persist_2);
  std::vector<std::pair<double,double>> p1;
  std::vector<std::pair<double,double>> p2;
  int p1_len = len(p1_list);
  int p2_len = len(p2_list);
  int deg = extract<int>(degree);
  int pow = extract<int>(power);
  for (int i=0; i < p1_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p1_list[i]);
    if (extract<int>(val[2]) == deg) {
      p1.push_back(std::pair<double,double>( extract<double>(val[0]), extract<double>(val[1])));
    }
  }
  for (int i=0; i < p2_len; ++i) {
    boost::python::list val = extract<boost::python::list>(p2_list[i]);
    if (extract<int>(val[2]) == deg) {
      p2.push_back(std::pair<double,double>( extract<double>(val[0]), extract<double>(val[1])));
    }
  }
  if (p1.size() != 0 and p2.size() != 0) {
    return geom_ws::wassersteinDist(p1,p2, pow, 0.01 /* relative error, 1% */, 
				    std::numeric_limits<double>::infinity() /* internal norm */);
  } else {
    return -1.0;
  }
}

