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



#include "relaxed_metric_space.h"

RelaxedMetricSpace::RelaxedMetricSpace(const SparsePoints & _points, const std::vector<double> & _deletionTimes, double _eps) : MetricSpace(_points.size())  {
	points = _points;
	deletion_times = _deletionTimes;
	eps = _eps;
	time_scale = 1;

	cached_distances = new double*[points.size()];
	for(int i = 0; i < points.size(); i++)  {
		cached_distances[i] = new double[points.size()];
		for(int j = 0; j < points.size(); j++)
			cached_distances[i][j] = -1;
	}
}

RelaxedMetricSpace::~RelaxedMetricSpace()  {
	for(int i = 0; i < points.size(); i++)
		delete [] cached_distances[i];
	delete [] cached_distances;
}

double RelaxedMetricSpace::distance(int _i, int _j)  {
	double numer_eps = 1e-15;
	std::pair<int,int> pairing = _i < _j ? std::pair<int,int>(_i,_j) : std::pair<int,int>(_j,_i);
	double local_dist = 0;
	/*
	if(distance_map.find(pairing) == distance_map.end())  {
		local_dist = points[_i].length(points[_j]);
		distance_map[pairing] = local_dist;
	}
	else
		local_dist = distance_map[pairing];
		*/
	int smaller_ind = _i < _j ? _i : _j;
	int larger_ind = _i > _j ? _i : _j;
	if(cached_distances[smaller_ind][larger_ind] == -1)  {
		local_dist = points[_i].length(points[_j]);
		cached_distances[smaller_ind][larger_ind] = local_dist;
	}
	else
		local_dist = cached_distances[smaller_ind][larger_ind];

	double t_p = time_scale*deletion_times[_i], t_q = time_scale*deletion_times[_j];
	if(t_q < t_p)  {
		double temp_t = t_p;
		t_p = t_q;
		t_q = temp_t;
	}
	if(local_dist <= (1-2*eps)*t_p)
		return local_dist;

	double alpha_1 = 2*local_dist - (1-2*eps)*t_p;
	if(alpha_1 > (1-2*eps)*t_p && alpha_1 < t_p && alpha_1 <= (1-2*eps)*t_q)
		return alpha_1;

	double alpha_2 = local_dist/(1-eps);
	if(alpha_2 >= (t_p-numer_eps) && alpha_2 <= ((1-2*eps)*t_q+numer_eps))
		return alpha_2;

	double alpha_3 = local_dist/(1-2*eps);
	if(alpha_3 >= t_p && alpha_3 >= t_q)
		return alpha_3;

	double alpha_4 = (local_dist-0.5*(1-2*eps)*t_q) / (0.5-eps);
	if(alpha_4 >= t_p && alpha_4 > (1-2*eps)*t_q && alpha_4 < t_q)
		return alpha_4;

	std::cout << "unknown alpha case! " << local_dist << " t_p: " << t_p << " ; t_q: " << t_q << std::endl;
	double min_alpha_p = (1-2*eps)*t_p, max_alpha_p = t_p;
	double min_alpha_q = (1-2*eps)*t_q, max_alpha_q = t_q;
	std::cout << "min alpha_p: " << min_alpha_p << " ; max alpha_p: " << max_alpha_p << " ; min alpha_q: " << min_alpha_q << " ; max alpha_q: " << max_alpha_q << std::endl;
	std::cout << "alpha_1: " << alpha_1 << " ; alpha_2: " << alpha_2 << " ; alpha_3: " << alpha_3 << " ; alpha_4: " << alpha_4 << std::endl;

	return alpha_1;
}
