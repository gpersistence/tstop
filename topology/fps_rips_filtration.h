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



#ifndef FPSRIPSFILTRATION_H
#define FPSRIPSFILTRATION_H

#include "rips_filtration.h"

class FPSRipsFiltration : public RipsFiltration {

	public:
		FPSRipsFiltration(const Points & _points, int _maxD, double _eps=1.5);
		FPSRipsFiltration(int _numPoints, double** _distanceMat, int _maxD, double _eps=1.5);
		~FPSRipsFiltration();

		virtual bool build_filtration();

	private:
		double eps;
		std::vector<double> deletion_times;

		void sparse_bron_kerbosch(std::vector<Simplex>* _rips, std::vector<int> _R, const std::set<int> & _P, int _maxD);

		void fps(int* sampling, double* fps_distances);
};

#endif
