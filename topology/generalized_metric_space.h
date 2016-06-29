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



#ifndef GENERALIZEDMETRICSPACE_H
#define GENERALIZEDMETRICSPACE_H

#include "metric_space.h"
#include <vector>

class GeneralizedMetricSpace : public MetricSpace {
	public:
		GeneralizedMetricSpace(int _numPoints, double** _distances);
		~GeneralizedMetricSpace();

		virtual double distance(int _i, int _j);

	private:
		double** distances;
};

#endif
