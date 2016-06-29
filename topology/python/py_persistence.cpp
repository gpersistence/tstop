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



//#include <Python.h>

#include "persistence.h"
#include "geometry/Vector.h"
#include "topology/filtration.h"
#include "topology/sparse_rips_filtration.h"
#include "topology/rips_filtration.h"
#include "topology/scale_space_kernel.h"
#include "topology/bottleneck_distance.h"
#include "topology/landscape_distance.h"
#include "topology/zero_persistence_python.h"
#include "topology/dtw_python.hpp"
#include "topology/rips_python.hpp"
#include <boost/make_shared.hpp>
#include <boost/python.hpp>

#include <iostream>

using namespace boost::python;

BOOST_PYTHON_MODULE(py_persistence)  {
  class_<Vector>("Vector", init<int>())
    .def("dim", &Vector::dim)
    .def("setEntry", &Vector::setEntry)
    .def("getEntry", &Vector::getEntry)
    .def("sqd_dist", &Vector::sqd_dist)
    .def("l2Norm", &Vector::l2Norm)
    ;

  class_<Filtration>("Filtration", no_init);
  class_<RipsFiltration, bases<Filtration> >("RipsFiltration", init<int,int>())
    .def("set_distance", &RipsFiltration::set_distance)
    .def("build_filtration", &Filtration::build_filtration)
    .def("build_metric", &RipsFiltration::build_metric)
    ;
  
  class_<SparseRipsFiltration, bases<Filtration> >("SparseRipsFiltration", init<int,double>())
    .def("set_max_simplices", &SparseRipsFiltration::set_max_simplices)
    .def("add_point", &SparseRipsFiltration::add_point)
    .def("set_random_seed", &SparseRipsFiltration::set_random_seed)
    .def("build_cover_tree", &SparseRipsFiltration::build_cover_tree)
    .def("build_filtration", &Filtration::build_filtration)
    .def("get_simplex_sparsity", &SparseRipsFiltration::get_simplex_sparsity)
    ;

  def("sparse_rips_filtration_generator", &RIPS_python::sparse_rips_filtration_generator, return_value_policy<manage_new_object>());
  def("rips_filtration_generator", &RIPS_python::rips_filtration_generator, return_value_policy<manage_new_object>());
  
  class_<PersistentPair>("PersistentPair", init<int,double,double>())
    .def("dim", &PersistentPair::dim)
    .def("birth_time", &PersistentPair::birth_time)
    .def("death_time", &PersistentPair::death_time)
    .def("persistence", &PersistentPair::persistence)
    .def("generator_size", &PersistentPair::generator_size)
    .def("get_generator_pt", &PersistentPair::get_generator_pt)
    ;
  
  class_<PersistenceDiagram>("PersistenceDiagram")
    .def("num_pairs", &PersistenceDiagram::num_pairs)
    .def("get_pair", &PersistenceDiagram::get_pair)
    .def("maximum_persistence", &PersistenceDiagram::maximum_persistence)
    .def("bottleneck_matcher", &PersistenceDiagram::bottleneck_matcher)
    .def("get_size_satisfied", &PersistenceDiagram::get_size_satisfied)
    ;
  
  class_<PersistentHomology>("PersistentHomology")
    .def("compute_persistence_sparse", &PersistentHomology::compute_persistence_sparse, return_value_policy<manage_new_object>())
    .def("compute_persistence_full", &PersistentHomology::compute_persistence_full, return_value_policy<manage_new_object>())
    ;

  class_<ZeroDimensionPersistence>("ZeroDimensionPersistence")
    .def("add_function_value", &ZeroDimensionPersistence::add_function_value)
    .def("sweep_persistence", &ZeroDimensionPersistence::sweep_persistence);

  def("ssk_similarity", &ScaleSpaceKernel::similarity);
  def("match_points", &BottleneckDistance::match_points);
  def("dtw_nearest_neighbor", &DTW_python::nearest_neighbor);
  def("dtw_distance", &DTW_python::distance);
  def("persistence_landscape_distance", &Landscape::distance);
  def("bottleneck_distance", &BottleneckDistance::bottleneck_distance);
  def("wasserstein_distance", &BottleneckDistance::wasserstein_distance);
}
