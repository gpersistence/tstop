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



#include "fps_rips_filtration.h"

FPSRipsFiltration::FPSRipsFiltration(const Points & _points, int _maxD, double _eps) : RipsFiltration(_points, _maxD) {
	eps = _eps;
}

FPSRipsFiltration::FPSRipsFiltration(int _numPoints, double** _distanceMat, int _maxD, double _eps) : RipsFiltration(_numPoints, _distanceMat, _maxD) {
	eps = _eps;
}

FPSRipsFiltration::~FPSRipsFiltration()  {
}

bool FPSRipsFiltration::build_filtration()  {
	// first construct farthest point sampling
	int* sampling = new int[num_points];
	double* fps_distances = new double[num_points];
	this->fps(sampling, fps_distances);

	// deletion times are (scaled) fps distances
	deletion_times = std::vector<double>(num_points,0);
	for(unsigned i = 0; i < num_points; i++)  {
		deletion_times[(sampling[i])] = fps_distances[i]*eps;
		//std::cout << "deletion times["<<sampling[i]<<"] : " << deletion_times[(sampling[i])] << std::endl;
	}

	delete [] sampling;
	delete [] fps_distances;

	// filtration is then cliques where points are not deleted
	if(all_simplices.size() > 0)
		all_simplices.clear();
	std::set<int> all_vertices;
	for(unsigned i = 0; i < num_points; i++)
		all_vertices.insert(i);
	this->sparse_bron_kerbosch(&all_simplices, std::vector<int>(), all_vertices, this->maxD());
	std::sort(all_simplices.begin(), all_simplices.end());

	bool do_verification = true;
	if(!do_verification)
		return true;

	std::vector<Simplex> full_filtration;
	all_vertices.clear();
	for(unsigned i = 0; i < num_points; i++)
		all_vertices.insert(i);
	this->global_bron_kerbosch(&full_filtration, std::vector<int>(), all_vertices, this->maxD());
	std::sort(full_filtration.begin(), full_filtration.end());

	std::set<std::string> sparse_simplex_ids;
	for(unsigned i = 0; i < all_simplices.size(); i++)
		sparse_simplex_ids.insert(all_simplices[i].unique_unoriented_id());

	for(unsigned idx = 0; idx < full_filtration.size(); idx++)  {
		Simplex simplex = full_filtration[idx];
		std::string simplex_id = simplex.unique_unoriented_id();

		bool exceeds_deletion_time = false;
		for(unsigned i = 0; i <= simplex.dim(); i++)  {
			for(unsigned j = 0; j < i; j++)  {
				double next_dist = distances[simplex.vertex(i)][simplex.vertex(j)];
				for(unsigned k = 0; k <= simplex.dim(); k++)  {
					if(next_dist > deletion_times[simplex.vertex(k)])  {
						exceeds_deletion_time = true;
						break;
					}
				}
				if(exceeds_deletion_time)
					break;
			}
			if(exceeds_deletion_time)
				break;
		}

		if(exceeds_deletion_time && sparse_simplex_ids.find(simplex_id) != sparse_simplex_ids.end())
			std::cout << "simplex " << simplex_id << " should not be included!" << std::endl;
		if(!exceeds_deletion_time && sparse_simplex_ids.find(simplex_id) == sparse_simplex_ids.end())
			std::cout << "simplex " << simplex_id << " should be included!" << std::endl;
	}
	return true;
}

void FPSRipsFiltration::sparse_bron_kerbosch(std::vector<Simplex>* _rips, std::vector<int> _R, const std::set<int> & _P, int _maxD)  {
	if(_R.size()!=0)
		_rips->push_back(Simplex(_R,metric_space));
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
		for(unsigned i = 0; i < R_new.size(); i++)  {
			for(unsigned j = 0; j < i; j++)  {
				double next_dist = distances[(R_new[i])][(R_new[j])];
				for(unsigned k = 0; k < R_new.size(); k++)  {
					if(next_dist > deletion_times[(R_new[k])])  {
						deletion_index = k;
						exceeds_deletion_time = true;
						break;
					}
				}
				if(exceeds_deletion_time)
					break;
			}
			if(exceeds_deletion_time)
				break;
		}

		if(exceeds_deletion_time)  {
			//std::cout << "removing element..." << std::endl;
			R_new.pop_back();
			continue;
		}

		this->sparse_bron_kerbosch(_rips, R_new, P_new, _maxD);
	}
}

void FPSRipsFiltration::fps(int* sampling, double* fps_distances)  {
	sampling[0] = rand() % num_points;
	fps_distances[0] = 1e15;

	double* minimum_distances = new double[num_points];
	for(int i = 0; i < num_points; i++)  {
		unsigned fp = sampling[0];
		minimum_distances[i] = distances[i][fp];
	}

	// add points one at a time, farthest in Euclidean distance from all other points
	std::cout << "farthest point sampling " << std::flush;
	int num_dots = 50 >= num_points ? (num_points-1) : 50;
	int dot_interval = num_points / num_dots;
	for(int i = 1; i < num_points; i++)  {
		if(i % dot_interval == 0)
			std::cout << "." << std::flush;
		double max_dist = -1e10;
		int best_ind = -1;

		// find minimum distance to all farthest points
		for(int p = 0; p < num_points; p++)  {
			if(minimum_distances[p] > max_dist)  {
				max_dist = minimum_distances[p];
				best_ind = p;
			}
		}

		// update minimum distances with newly added point
		for(int j = 0; j < num_points; j++)  {
			double new_dist = distances[j][best_ind];
			minimum_distances[j] = new_dist < minimum_distances[j] ? new_dist : minimum_distances[j];
		}

		sampling[i] = best_ind;
		fps_distances[i] = max_dist;
	}
	std::cout << std::endl;
	delete [] minimum_distances;
}
