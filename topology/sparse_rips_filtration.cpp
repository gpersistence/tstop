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



#include "sparse_rips_filtration.h"

SparseRipsFiltration::SparseRipsFiltration(const Points & _points, std::vector<int> _levels, std::vector<int> _parents, int _maxD, double _eps) : Filtration(_maxD) {
	for(int i = 0; i < _points.size(); i++)  {
		Vector next_pt = _points[i];
		std::vector<int> nonzero_inds;
		std::vector<double> nonzero_values;
		for(int j = 0; j < next_pt.dim(); j++)  {
		//	if(next_pt[j] != 0)  {
				nonzero_inds.push_back(j);
				nonzero_values.push_back(next_pt[j]);
		//	}
		}
		points.push_back(SparseVector(nonzero_inds,nonzero_values,next_pt.dim()));
	}
	eps = _eps;
	num_points = points.size();

	cover_tree = new CoverTree(points, _levels, _parents);
	this->build_point_weights();
	metric_space = new RelaxedMetricSpace(points, deletion_times, eps);

	is_initialized = true;
	max_simplices = 0;
}

SparseRipsFiltration::SparseRipsFiltration(const Points & _points, int _maxD, double _eps) : Filtration(_maxD) {
	for(int i = 0; i < _points.size(); i++)  {
		Vector next_pt = _points[i];
		std::vector<int> nonzero_inds;
		std::vector<double> nonzero_values;
		for(int j = 0; j < next_pt.dim(); j++)  {
			//if(next_pt[j] != 0)  {
				nonzero_inds.push_back(j);
				nonzero_values.push_back(next_pt[j]);
			//}
		}
		points.push_back(SparseVector(nonzero_inds,nonzero_values,next_pt.dim()));
	}
	eps = _eps;
	num_points = points.size();

	this->build_cover_tree();
	max_simplices = 0;
}

SparseRipsFiltration::SparseRipsFiltration(int _maxD, double _eps) : Filtration(_maxD) {
	eps = _eps;
	num_points = 0;
	is_initialized = false;
	max_simplices = 0;
}

SparseRipsFiltration::~SparseRipsFiltration()  {
	if(is_initialized)  {
		std::cout << "deleting cover tree..." << std::endl;
		//delete cover_tree;
		std::cout << "deleting metric space..." << std::endl;
		delete metric_space;
		std::cout << "done with deletion" << std::endl;
	}
}

void SparseRipsFiltration::add_point(const Vector & _pt)  {
	std::vector<int> nonzero_inds;
	std::vector<double> nonzero_values;
	for(int j = 0; j < _pt.dim(); j++)  {
		//if(_pt[j] != 0)  {
			nonzero_inds.push_back(j);
			nonzero_values.push_back(_pt[j]);
		//}
	}
	points.push_back(SparseVector(nonzero_inds,nonzero_values,_pt.dim()));
	num_points++;
}

void SparseRipsFiltration::build_cover_tree()  {
	cover_tree = new CoverTree(points, 2);
	cover_tree->build_tree();
	this->build_point_weights();
	metric_space = new RelaxedMetricSpace(points, deletion_times, eps);

	is_initialized = true;
}

void SparseRipsFiltration::build_point_weights()  {
	// deletion times follow from Sheehy's paper
	deletion_times = std::vector<double>(num_points,0);
	for(int i = 0; i < num_points; i++)
		deletion_times[i] = 1.0/(eps*(1.0-2*eps)) * cover_tree->parent_radius(i);
		//deletion_times[i] = ((double)rand()/(double)RAND_MAX)*cover_tree->parent_radius(i);
}

void SparseRipsFiltration::set_random_seed(int _seed)  {
	srand(_seed);
}

bool SparseRipsFiltration::build_filtration()  {
	// filtration is cliques where points are not deleted, but also using the relaxed distance
	if(all_simplices.size() > 0)
		all_simplices.clear();

	std::vector<IndexedDouble> sorted_vertices;
	for(int i = 0; i < num_points; i++)
		sorted_vertices.push_back(IndexedDouble(i, metric_space->get_deletion_time(i)));
	std::sort(sorted_vertices.begin(),sorted_vertices.end());

	bool size_satisfied = false;
	if(max_simplices == 0)  {
		std::set<int> vertex_set;
		for(int i = 0; i < num_points; i++)
			vertex_set.insert(sorted_vertices[i].ind);
		metric_space->set_time_scale(1);
		this->sparse_bron_kerbosch(&all_simplices, vertex_set, 2);
		int num_simplices = all_simplices.size();
		std::cout << "total number of simplices: " << num_simplices << std::endl;
		size_satisfied = true;
	}
	else  {
		int iteration = 0;
		double upper_scale = 2, lower_scale = 0;
		while(!size_satisfied)  {
			all_simplices.clear();
			std::set<int> vertex_set;
			for(int i = 0; i < num_points; i++)
				vertex_set.insert(sorted_vertices[i].ind);
			metric_space->set_time_scale(0.5*(upper_scale+lower_scale));
			this->sparse_bron_kerbosch(&all_simplices, vertex_set, 2);
			int num_simplices = all_simplices.size();
			std::cout << "total number of simplices["<<iteration<<"]: " << num_simplices << "; scale: " << metric_space->get_time_scale() << " ("<<lower_scale<<","<<upper_scale<<")"<<std::endl;

			if(max_simplices == 0)  {
				size_satisfied = true;
				break;
			}

			if(iteration == 0 && num_simplices < max_simplices)  {
				size_satisfied = true;
				break;
			}

			if (iteration >= 50) {
				size_satisfied = true;
				std::cout << "filtration iteration too high, bailing" << std::endl;
				break;
			}

			double size_ratio = (double)(num_simplices-max_simplices) / max_simplices;
			if(size_ratio < 0.05 && num_simplices > max_simplices)  {
				size_satisfied = true;
				break;
			}

			if(num_simplices < max_simplices)  {
				lower_scale = 0.5*(upper_scale+lower_scale);
			}
			else  {
				upper_scale = 0.5*(upper_scale+lower_scale);
			}

			iteration++;
		}
	}

	/*
	vertex_set.clear();
	for(int i = 0; i < num_points; i++)
		vertex_set.insert(sorted_vertices[i].ind);
	ComputationTimer bf_bk("brute force bron kerbosch");
	bf_bk.start();
	std::cout << "brute force bron kerbosch..." << std::endl;
	this->bf_bron_kerbosch(&all_simplices, std::vector<int>(), vertex_set, 2);
	std::cout << "... done with brute force bron kerbosch... " << all_simplices.size() << std::endl;
	bf_bk.end();
	bf_bk.dump_time();
	*/

	for(int s = 0; s < all_simplices.size(); s++)
		all_simplices[s].compute_simplex_distance();
	std::sort(all_simplices.begin(), all_simplices.end());

	std::vector<int> simplex_count(this->maxD()+1,0);
	for(int i = 0; i < all_simplices.size(); i++)  {
		simplex_count[all_simplices[i].dim()]=simplex_count[all_simplices[i].dim()]+1;
	}
	for(int i = 0; i < simplex_count.size(); i++)  {
		long max_num_simplices = num_points;
		for(int j = 1; j <= i; j++)
			max_num_simplices *= (num_points-j);
		for(int j = 1; j <= i; j++)
			max_num_simplices /= (j+1);
		std::cout << "number of " << i << " simplices: " << simplex_count[i] << " / " << max_num_simplices << " ; sparsity: " << 100.0*((double)simplex_count[i]/max_num_simplices) << "%" << std::endl;
		simplex_sparsity.push_back(((double)simplex_count[i]/max_num_simplices));
	}
	return size_satisfied;
}

void SparseRipsFiltration::bf_bron_kerbosch(std::vector<Simplex>* _rips, std::vector<int> _R, const std::set<int> & _P, int _maxD)  {
	if(max_simplices != 0 && _rips->size() > 2*max_simplices)
		return;

	if(_R.size()!=0)  {
		_rips->push_back(Simplex(_R,metric_space));
	}
	if(_R.size() == (_maxD+1))
		return;

	std::set<int> P_new = _P;
	for(std::set<int>::iterator i_it = _P.begin(); i_it != _P.end(); ++i_it)  {
		int v = *(i_it);
		std::vector<int> R_new = _R;
		R_new.push_back(v);
		P_new.erase(v);

		// check if any edges in this simplex exceed deletion times -> don't include simplex, and all subsequent simplices, if so
		bool exceeds_deletion_time = false;
		int deletion_index = -1;
		for(int i = 0; i < R_new.size(); i++)  {
			for(int j = 0; j < i; j++)  {
				double next_dist = metric_space->distance(R_new[i],R_new[j]);
				double t_i = metric_space->get_deletion_time(R_new[i]), t_j = metric_space->get_deletion_time(R_new[j]);
				double min_deletion_time = t_i < t_j ? t_i : t_j;
				if(next_dist > min_deletion_time)  {
					exceeds_deletion_time = true;
					break;
				}
				/*
				for(int k = 0; k < R_new.size(); k++)  {
					if(next_dist > metric_space->get_deletion_time(R_new[k]))  {
						deletion_index = k;
						exceeds_deletion_time = true;
						break;
					}
				}
				if(exceeds_deletion_time)
					break;
				*/
			}
			if(exceeds_deletion_time)
				break;
		}

		if(exceeds_deletion_time)  {
			//std::cout << "removing element..." << std::endl;
			R_new.pop_back();
			continue;
		}

		this->bf_bron_kerbosch(_rips, R_new, P_new, _maxD);

		if(max_simplices != 0 && _rips->size() > 2*max_simplices)
			return;
	}
}

void SparseRipsFiltration::sparse_bron_kerbosch(std::vector<Simplex>* _rips, std::set<int> _P, int _maxD)  {
	// first add all vertices as 0-simplices
	for(std::set<int>::iterator i_it = _P.begin(); i_it != _P.end(); ++i_it)  {
		std::vector<int> single_R;
		single_R.push_back(*i_it);
		_rips->push_back(Simplex(single_R,metric_space));
	}

	// for each vertex, find all possible 1-simplices: all subsequent cliques will be subsets of this set
	for(std::set<int>::iterator i_it = _P.begin(); i_it != _P.end(); ++i_it)  {
		int v = *i_it;
		std::set<int> P_candidate = _P;
		//std::set<int> P_candidate = cover_tree->ball_query(points[v],metric_space->get_deletion_time(v));
		//std::cout << "P_candidate["<<v<<"] number of points queried: " << P_candidate.size() << " / " << _P.size() << std::endl;

		std::set<int> P;
		for(std::set<int>::iterator i_it = P_candidate.begin(); i_it != P_candidate.end(); ++i_it)  {
			int cand_v = *(i_it);
			if(cand_v <= v)
				continue;
			double proper_time = metric_space->get_deletion_time(cand_v) < metric_space->get_deletion_time(v) ? metric_space->get_deletion_time(cand_v) : metric_space->get_deletion_time(v);
			if(metric_space->distance(v,cand_v) > proper_time)
				continue;
			P.insert(cand_v);
		}

		std::set<int> P_new = P;
		std::vector<int> R;
		R.push_back(v);
		for(std::set<int>::iterator i_it = P.begin(); i_it != P.end(); ++i_it)  {
			int q = *(i_it);
			std::vector<int> R_new = R;
			R_new.push_back(q);
			P_new.erase(q);
			this->bf_bron_kerbosch(_rips, R_new, P_new, _maxD);
		}

		if(max_simplices != 0 && _rips->size() > 2*max_simplices)
			return;
	}
}
