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



#ifndef RIPSFILTRATION_H
#define RIPSFILTRATION_H

#include "filtration.h"
#include "generalized_metric_space.h"

class RipsFiltration : public Filtration  {
	public:
		RipsFiltration(const Points & _points, int _maxD);
		RipsFiltration(int _numPoints, double** _distanceMat, int _maxD);
		RipsFiltration(int _numPoints, int _maxD);
		~RipsFiltration();

		void global_bron_kerbosch(std::vector<Simplex>* _rips, std::vector<int> _R, const std::set<int> & _P, int _maxD);

		virtual bool build_filtration();


    void set_distance(int _i, int _j, double _v);
    void build_metric();

	protected:
		int num_points;
		double** distances;
		MetricSpace* metric_space;

	private:
};

#endif
