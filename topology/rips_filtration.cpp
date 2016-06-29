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



#include "rips_filtration.h"


RipsFiltration::RipsFiltration(const Points & _points, int _maxD) : Filtration(_maxD)  {
	num_points = _points.size();
	distances = new double*[num_points];
	for(int i = 0; i < num_points; i++)  {
		distances[i] = new double[num_points];
		distances[i][i] = 0;
		for(int j = 0; j < i; j++)  {
			distances[i][j] = (_points[i]-_points[j]).l2Norm();
			distances[j][i] = distances[i][j];
		}
	}
	metric_space = new GeneralizedMetricSpace(num_points, distances);
}

RipsFiltration::RipsFiltration(int _numPoints, int _maxD) : Filtration(_maxD)  {
  num_points = _numPoints;
	distances = new double*[num_points];
	for(int i = 0; i < num_points; i++)  {
		distances[i] = new double[num_points];
    distances[i][i] = 0;
  }
}

RipsFiltration::RipsFiltration(int _numPoints, double** _distanceMat, int _maxD) : Filtration(_maxD)  {
	num_points = _numPoints;
	distances = new double*[num_points];
	for(int i = 0; i < num_points; i++)  {
		distances[i] = new double[num_points];
		distances[i][i] = 0;
		for(int j = 0; j < i; j++)  {
			distances[i][j] = _distanceMat[i][j];
			distances[j][i] = distances[i][j];
		}
	}
	metric_space = new GeneralizedMetricSpace(num_points, distances);
}

RipsFiltration::~RipsFiltration()  {
	for(int i = 0; i < num_points; i++)
		delete [] distances[i];
	delete [] distances;
	delete metric_space;
}

void RipsFiltration::set_distance(int _i, int _j, double _v) {
  distances[_i][_j] = _v;
  distances[_j][_i] = _v;
}

void RipsFiltration::build_metric() {
	metric_space = new GeneralizedMetricSpace(num_points, distances);
}

void RipsFiltration::global_bron_kerbosch(std::vector<Simplex>* _rips, std::vector<int> _R, const std::set<int> & _P, int _maxD)  {
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
		this->global_bron_kerbosch(_rips, R_new, P_new, _maxD);
	}
}

bool RipsFiltration::build_filtration()  {
	if(all_simplices.size() > 0)
		all_simplices.clear();
	std::set<int> all_vertices;
	for(int i = 0; i < num_points; i++)
		all_vertices.insert(i);
	this->global_bron_kerbosch(&all_simplices, std::vector<int>(), all_vertices, this->maxD());
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
		std::cout << "number of " << i << " simplices: " << simplex_count[i] << std::endl;
	}

	return true;
}
