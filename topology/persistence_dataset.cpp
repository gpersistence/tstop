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



#include "persistence_dataset.h"

PersistenceDataset::PersistenceDataset(std::string _filename, double _trainingPerc)  {
	training_perc = _trainingPerc;
	std::ifstream pds_file(_filename.c_str());
	if(pds_file.fail())  {
		std::cerr << "bad persistence diagrams filename! " << _filename << std::endl;
		return;
	}

	std::map<std::string,int> label_mapping;
	int line_length = 50*1024*1024;
	char* line_raw = new char[line_length];
	for(;;)  {
		pds_file.getline(line_raw, line_length);
		if(pds_file.eof())
			break;

		std::string line(line_raw);
		std::vector<std::string> tokens;
		this->tokenize_line(&tokens, line, ",");

		std::string label_name = tokens[0];
		if(label_mapping.find(label_name) == label_mapping.end())
			label_mapping[label_name] = label_mapping.size();
		int label_id = label_mapping[label_name];
		std::vector<PersistentPair> all_pairs;
		for(int i = 1; i < tokens.size(); i+=3)  {
			int dim = atoi(tokens[i].c_str());
			double birth = atof(tokens[i+1].c_str()), death = atof(tokens[i+2].c_str());
			all_pairs.push_back(PersistentPair(dim,birth,death));
		}
		labeled_persistence_diagrams.push_back(LabeledPersistenceDiagram(PersistenceDiagram(all_pairs),label_id));
		all_labels.insert(label_id);
	}

	pds_file.close();
}

PersistenceDataset::~PersistenceDataset()  {}

void PersistenceDataset::training_shuffle()  {
	if(training_inds.size() > 0)  {
		training_inds.clear();
		test_inds.clear();
	}

	int num_training = labeled_persistence_diagrams.size()*training_perc;
	std::vector<int> permuted_inds;
	for(int i = 0; i < labeled_persistence_diagrams.size(); i++)
		permuted_inds.push_back(i);
	for(int i = 0; i < num_training; i++)  {
		int rand_ind = rand() % (labeled_persistence_diagrams.size()-i);
		int permuted_index = permuted_inds[rand_ind];
		training_inds.push_back(permuted_index);
		permuted_inds[rand_ind] = permuted_inds[labeled_persistence_diagrams.size()-i-1];
	}
	for(int i = num_training; i < labeled_persistence_diagrams.size(); i++)  {
		int rand_ind = rand() % (labeled_persistence_diagrams.size()-i);
		int permuted_index = permuted_inds[rand_ind];
		test_inds.push_back(permuted_index);
		permuted_inds[rand_ind] = permuted_inds[labeled_persistence_diagrams.size()-i-1];
	}
}

void PersistenceDataset::tokenize_line(std::vector<std::string>* tokens, const std::string& input, std::string sep)  {
	std::string comm;
	for (int i = 0; i < input.size(); i++)  {
		const char ch = input[i];
		bool added = false;
		for (int s = 0; s < sep.size(); s++)  {
			if (ch == sep[s])  {
				if(comm.size() > 0)
					tokens->push_back(comm);
				comm = "";
				added = true;
				break;
			}
		}
		if (!added)
			comm += ch;
	}
	if (comm != "")
		tokens->push_back(comm);
}
