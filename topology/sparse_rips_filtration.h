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



#ifndef SPARSERIPSFILTRATION_H
#define SPARSERIPSFILTRATION_H

#include "filtration.h"
#include "ComputationTimer.h"
#include "../geometry/covertree.h"
#include <list>
#include "relaxed_metric_space.h"

class SparseRipsFiltration : public Filtration {

	public:
		SparseRipsFiltration(const Points & _points, std::vector<int> _levels, std::vector<int> _parents, int _maxD, double _eps=1/3.0);
		SparseRipsFiltration(const Points & _points, int _maxD, double _eps=1/3.0);
		SparseRipsFiltration(int _maxD, double _eps=1/3.0);
		~SparseRipsFiltration();

		void build_cover_tree();
		virtual bool build_filtration();

		void set_max_simplices(int _maxSimplices)  { max_simplices = _maxSimplices; }

		void add_point(const Vector & _pt);

		void set_random_seed(int _seed);

		double get_simplex_sparsity(int _i)  { return simplex_sparsity[_i]; }

	private:
		double eps;
		SparsePoints points;
		std::vector<double> deletion_times;
		CoverTree* cover_tree;

		bool is_initialized;

		int max_simplices;
		int num_points;
		RelaxedMetricSpace* metric_space;
		std::vector<double> simplex_sparsity;

		void bf_bron_kerbosch(std::vector<Simplex>* _rips, std::vector<int> _R, const std::set<int> & _P, int _maxD);
		void sparse_bron_kerbosch(std::vector<Simplex>* _rips, std::set<int> _P, int _maxD);

		void build_point_weights();
		void build_modified_distances();
};

#endif
