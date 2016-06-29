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



#ifndef PERSISTENCE_H
#define PERSISTENCE_H

#include "persistence_diagram.h"

#include "filtration.h"
#include "sparse_rips_filtration.h"
#include "rips_filtration.h"
#include <list>
#include <map>
#include "ComputationTimer.h"

typedef std::list<int> PHCycle;

class PersistentHomology  {
	public:
		PersistentHomology(bool _retainGenerators=false);
		PersistentHomology(Filtration* _filtration, bool _retainGenerators=false);
		~PersistentHomology();

		PersistenceDiagram *compute_persistence_sparse(SparseRipsFiltration *, int _maxD);
		PersistenceDiagram *compute_persistence_full(RipsFiltration *, int _maxD);

		PHCycle merge_cycles(const PHCycle & _c1, const PHCycle & _c2);

	private:
		Filtration* filtration;
		int max_d;
		bool retain_generators;

		std::list<int> expand_chain(int _chain, PHCycle* _allChains);
};

#endif
