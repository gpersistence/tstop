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



#ifndef SPARSEPERSISTENCE_H
#define SPARSEPERSISTENCE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <iostream>
#include <algorithm>
#include <vector>
#include <assert.h>
#include <map>
#include <sstream>
#include <list>

#include "../geometry/point_incs.h"
#include "persistence_diagram.h"

using namespace std;

#define CHRIS_VERBOSE 0

typedef struct sinf {
	string str;//TODO: Make this a pointer?
	size_t index;
	size_t k;//Number of vertices in the simplex
	double dist;
} SimplexInfo;

typedef struct bdt {
	double birth;
	double death;
} BDTimes;

struct Simplex_DistComparator {
	bool operator()(SimplexInfo* s1, SimplexInfo* s2) const {
		if (s1->dist < s2->dist) {
			return true;
		}
		else if (s1->dist == s2->dist) {
			//Make sure to add the faces of a simplex before adding the simplex
			return s1->k < s2->k;
		}
		return false;
	}
};

class SparsePersistence  {
	public:
		SparsePersistence(const Points & _points, const std::vector<int> & _levels, double _ctScale, int _maxD);
		~SparsePersistence();

		void printMatrix(vector<int>* M, int n, int m);
		double getSqrDist(int i, int j);
		void getEdgeRelaxedDist(int p, int q, double* ts, int* e1, int* e2, double* ed);
		void getEdgeUnwarpedDist(int p, int q, double* ts, int* e1, int* e2, double* ed);
		void getCoDim1CliqueStrings(vector<string>& cocliques, string str);
		void addCliquesFromProximityList(vector<int>& Ep, map<string, double>& EDists, map<string, SimplexInfo>* simplices, int MaxBetti);
		void addColToColMod2(vector<int>& col1, vector<int>& col2);
		void addLowElementToOthers(vector<int>* M, int col, list<int>& nzc);
		PersistenceDiagram compute_persistence();

	private:
		int max_d;
		Points points;
		std::vector<int> levels;
		double ct_scale;
};

#endif
