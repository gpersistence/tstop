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



#ifndef PERSISTENCE_DATASET_H
#define PERSISTENCE_DATASET_H

#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdlib.h>

#include "persistence_diagram.h"

class PersistenceDataset  {
	public:
		PersistenceDataset(std::string _filename, double _trainingPerc=0.5);
		~PersistenceDataset();

		int size()  { return labeled_persistence_diagrams.size(); }
		LabeledPersistenceDiagram get_pd(int _i)  { return labeled_persistence_diagrams[_i]; }

		void training_shuffle();

		int training_size()  {
			return training_inds.size();
		}

		std::vector<int> get_training_inds()  { return training_inds; }
		std::vector<int> get_test_inds()  { return test_inds; }

		LabeledPersistenceDiagram get_training_pd(int _i) const  {
			return labeled_persistence_diagrams[(training_inds[_i])];
		}

		int test_size()  {
			return test_inds.size();
		}

		LabeledPersistenceDiagram get_test_pd(int _i) const  {
			return labeled_persistence_diagrams[(test_inds[_i])];
		}

	private:
		double training_perc;
		std::vector<LabeledPersistenceDiagram> labeled_persistence_diagrams;
		std::set<int> all_labels;
		std::vector<int> training_inds;
		std::vector<int> test_inds;

		void tokenize_line(std::vector<std::string>* tokens, const std::string& input, std::string sep);
};

#endif
