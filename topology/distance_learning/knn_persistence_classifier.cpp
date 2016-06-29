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



#include "knn_persistence_classifier.h"

KNNPersistenceClassifier::KNNPersistenceClassifier(const std::vector<LabeledPersistenceDiagram> & _trainingPDs, const std::vector<int> & _trainingInds)  {
	training_pds = _trainingPDs;
	training_inds = _trainingInds;

	// extract possible labels
	for(int i = 0; i < training_pds.size(); i++)
		all_labels.insert(training_pds[i].label);
}

KNNPersistenceClassifier::~KNNPersistenceClassifier()  {
}

int KNNPersistenceClassifier::knn_prediction(const PersistenceDiagram & _testPD, int _d, int _k)  {
	std::vector<IndexedDouble> sorted_persistence;
	for(int i = 0; i < _testPD.num_pairs(); i++)  {
		PersistentPair pair = _testPD.get_pair(i);
		if(pair.dim() != _d)
			continue;
		double persistence = _testPD.get_pair(i).l_inf_diagonal();
		sorted_persistence.push_back(IndexedDouble(i,persistence));
	}
	std::sort(sorted_persistence.begin(),sorted_persistence.end());
	/*
	for(int i = 0; i < sorted_persistence.size(); i++)  {
		std::cout << "distance to diagonal["<<i<<"] : " << sorted_persistence[i].value << std::endl;
	}
	*/

	// compute bottleneck distance between this persistence diagram and all training PDs
	std::vector<IndexedDouble> sorted_neighbors(training_pds.size(),IndexedDouble(0,0));
	int i = 0;
//#pragma omp parallel for
	for(i = 0; i < training_pds.size(); i++)  {
		//std::cout << "wasserstein distance for PD " << i << " ; " << training_pds[i].pd.num_pairs() << " : " << _testPD.num_pairs() << " ..." << std::endl;
		double wasserstein_distance = training_pds[i].pd.wasserstein_distance(_testPD,_d,1);
		//std::cout << "wasserstein distance["<<i<<"] : " << wasserstein_distance << std::endl;
		sorted_neighbors[i] = IndexedDouble(i,wasserstein_distance);
	}

	// sort, do knn classification
	std::sort(sorted_neighbors.begin(),sorted_neighbors.end());
	std::map<int,int> label_votes;
	for(std::set<int>::iterator label_iter = all_labels.begin(); label_iter != all_labels.end(); ++label_iter)
		label_votes[*label_iter] = 0;
	for(int k = 0; k < _k; k++)  {
		int neighbor_label = training_pds[sorted_neighbors[k].ind].label;
		label_votes[neighbor_label]=label_votes[neighbor_label]+1;
		std::cout << "neighbor label["<<k<<"] : " << neighbor_label << " -> " << sorted_neighbors[k].value << " ; " << training_inds[sorted_neighbors[k].ind] << std::endl;
		/*
		int pd_ind = sorted_neighbors[k].ind;
		std::cout << "persistence pairings:" << std::endl;
		for(int i = 0; i < training_pds[pd_ind].pd.num_pairs(); i++)  {
			PersistentPair pairing = training_pds[pd_ind].pd.get_pair(i);
			if(pairing.d != 1)
				continue;
			std::cout << "( " << pairing.birth << " , " << pairing.death << " )" << std::endl;
		}
		*/
	}
	int highest_count = 0, predicted_label = 0;
	for(std::set<int>::iterator label_iter = all_labels.begin(); label_iter != all_labels.end(); ++label_iter)  {
		int next_label = *label_iter;
		if(label_votes[next_label] > highest_count)  {
			highest_count = label_votes[next_label];
			predicted_label = next_label;
		}
	}

	return predicted_label;
}
