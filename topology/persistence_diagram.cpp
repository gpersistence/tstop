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



#include "persistence_diagram.h"

PersistenceDiagram::PersistenceDiagram(std::string _filename)  {
	Points points;
	PointsIO::read_points_from_file(_filename, points);
	for(int i = 0; i < points.size(); i++)  {
		Vector pt = points[i];
		int dim = pt[0];
		double birth = pt[1];
		double death = pt[2];
		PersistentPair persistence_pair(dim,birth,death);

		if(pt.dim() > 3)  {
			for(int j = 3; j < pt.dim(); j++)
				persistence_pair.add_generator_pt(pt[j]);
		}
		all_pairs.push_back(persistence_pair);
	}
	_size_satisfied = true;
}

PersistenceDiagram::PersistenceDiagram(const std::vector<PersistentPair> & _allPairs)  {
	all_pairs = _allPairs;
	_size_satisfied = true;
}

PersistenceDiagram::~PersistenceDiagram()  {
	_size_satisfied = true;
}

double PersistenceDiagram::bottleneck_distance(const PersistenceDiagram & _otherPD, int _d) const {
	std::vector<PersistentPair> our_pairs = this->get_persistence_pairs(_d);
	std::vector<PersistentPair> other_pairs = _otherPD.get_persistence_pairs(_d);
	unsigned max_size = our_pairs.size() + other_pairs.size();

	// Compute all the edges and sort them by distance
	EdgeVector edges;

	// Connect all diagonal points to each other
	for(unsigned i = our_pairs.size(); i < max_size; i++)  {
		for(unsigned j = max_size + other_pairs.size(); j < 2*max_size; ++j)
			edges.push_back(WeightedEdge(i, j, 0));
	}

	// Edges between real points
	for(unsigned i = 0; i < our_pairs.size(); i++)  {
		for(unsigned j = 0; j < other_pairs.size(); j++)  {
			double weight = our_pairs[i].l_inf_norm(other_pairs[j]);
			edges.push_back(WeightedEdge(i,max_size+j, weight));
		}
	}

   // Edges between real points and their corresponding diagonal points
	for(unsigned i = 0; i < our_pairs.size(); i++)
		edges.push_back(WeightedEdge(i, (max_size+other_pairs.size()+i), our_pairs[i].l_inf_diagonal()));
	for(unsigned i = 0; i < other_pairs.size(); i++)
		edges.push_back(WeightedEdge(our_pairs.size()+i, max_size+i, other_pairs[i].l_inf_diagonal()));
	std::sort(edges.begin(), edges.end());

   // Perform cardinality based binary search
	typedef boost::counting_iterator<EV_const_iterator>         EV_counting_const_iterator;
	EV_counting_const_iterator bdistance = std::upper_bound(EV_counting_const_iterator(edges.begin()), EV_counting_const_iterator(edges.end()), edges.begin(),
			CardinalityComparison(max_size, edges.begin()));
	return (*bdistance)->distance;
}

std::pair<std::vector<int>,std::vector<int> > PersistenceDiagram::bottleneck_matcher(const PersistenceDiagram & _otherPD, int _d) const {
	std::vector<PersistentPair> our_pairs = this->get_persistence_pairs(_d);
	std::vector<PersistentPair> other_pairs = _otherPD.get_persistence_pairs(_d);
	int max_size = our_pairs.size() + other_pairs.size();

	// Compute all the edges and sort them by distance
	EdgeVector edges;
	std::map<std::pair<int,int>, double> all_weights;

	int our_start = 0, our_diag_start = our_pairs.size(), other_start = max_size, other_diag_start = max_size+other_pairs.size(), end = 2*max_size;
	// Connect all diagonal points to each other
	for(int i = our_pairs.size(); i < max_size; i++)  {
		for(int j = max_size + other_pairs.size(); j < 2*max_size; ++j)
			edges.push_back(WeightedEdge(i, j, 0));
	}

	// Edges between real points
	for(int i = 0; i < our_pairs.size(); i++)  {
		for(int j = 0; j < other_pairs.size(); j++)  {
			double weight = our_pairs[i].l_inf_norm(other_pairs[j]);
			edges.push_back(WeightedEdge(i,max_size+j, weight));
			all_weights[std::pair<int,int>(i,j)] = weight;
		}
	}
   
   // Edges between real points and their corresponding diagonal points
	for(int i = 0; i < our_pairs.size(); i++)
		edges.push_back(WeightedEdge(i, (max_size+other_pairs.size()+i), our_pairs[i].l_inf_diagonal()));
	for(int i = 0; i < other_pairs.size(); i++)
		edges.push_back(WeightedEdge(our_pairs.size()+i, max_size+i, other_pairs[i].l_inf_diagonal()));
	std::sort(edges.begin(), edges.end());

   // Perform cardinality based binary search
	typedef boost::counting_iterator<EV_const_iterator>         EV_counting_const_iterator;
	EV_counting_const_iterator first = EV_counting_const_iterator(edges.begin());
	EV_counting_const_iterator last = EV_counting_const_iterator(edges.end());
	CardinalityComparison comparator(max_size, edges.begin());

	EV_counting_const_iterator it;
	typename std::iterator_traits<EV_counting_const_iterator>::difference_type count, step;
	count = std::distance(first,last);

	MatchingVector bottleneck_matching;
	while (count > 0) {
		it = first; 
		step = count / 2; 
		std::advance(it, step);
		if (!(comparator(edges.begin(),*it))) {
			first = ++it;
			count -= step + 1;
		}
		else  {
			count = step;
			bottleneck_matching = comparator.mates;
		}
	}

	int num_src_unassigned = 0, num_dst_unassigned = 0;
	int num_src_diag_unassigned = 0, num_dst_diag_unassigned = 0;
	int src_id_unassigned = -1, dst_id_unassigned = -1;
	std::vector<int> src_matches(our_pairs.size(),-1);
	std::vector<int> dst_matches(other_pairs.size(),-1);
	for(int i = our_start; i < our_diag_start; i++)  {
		int the_match = bottleneck_matching[i];
		if(the_match >= other_start && the_match < other_diag_start)
			src_matches[i-our_start] = the_match-other_start;
		else if(the_match >= other_diag_start && the_match < end)
			src_matches[i-our_start] = -1;
		else  {
			num_src_unassigned++;
			src_id_unassigned = i-our_start;
		}
	}
	for(int i = our_diag_start; i < other_start; i++)  {
		int diag_match = bottleneck_matching[i];
		if(diag_match < other_start || diag_match >= end)
			num_src_diag_unassigned++;
	}
	for(int i = other_start; i < other_diag_start; i++)  {
		int the_match = bottleneck_matching[i];
		if(the_match >= our_start && the_match < our_diag_start)
			dst_matches[i-other_start] = the_match-our_start;
		else if(the_match >= our_diag_start && the_match < other_start)
			dst_matches[i-other_start] = -1;
		else  {
			num_dst_unassigned++;
			dst_id_unassigned = i-other_start;
		}
	}
	for(int i = other_diag_start; i < end; i++)  {
		int diag_match = bottleneck_matching[i];
		if(diag_match < our_start || diag_match >= other_start)
			num_dst_diag_unassigned++;
	}

	//std::cout << "unassigned: " << num_src_unassigned << " : " << num_src_diag_unassigned << " : " << num_dst_unassigned << " : " << num_dst_diag_unassigned << std::endl;
	if(num_src_unassigned > 1 || num_dst_unassigned > 1)  {
		std::cout << "BADNESS! MORE THAN ONE UNASSIGNMENT!!! " << num_src_unassigned << " : " << num_dst_unassigned << std::endl;
		return std::pair<std::vector<int>, std::vector<int> >(src_matches,dst_matches);
	}
	else if(num_src_unassigned == 1 && num_dst_diag_unassigned == 1)
		std::cout << "missing src assignment, probably just diagonal..." << std::endl;
	else if(num_dst_unassigned == 1 && num_src_diag_unassigned == 1)
		std::cout << "missing dst assignment, probably just diagonal..." << std::endl;
	else if(num_src_unassigned == 1 && num_dst_unassigned == 1)  {
		src_matches[src_id_unassigned] = dst_id_unassigned;
		dst_matches[dst_id_unassigned] = src_id_unassigned;
		std::cout << "dangling assignment: " << src_id_unassigned << " : " << dst_id_unassigned << std::endl;
	}

	double largest_cost = -1;
	for(int s = 0; s < src_matches.size(); s++)  {
		double edge_cost = -1;
		if(src_matches[s] == -1)  {
			edge_cost = our_pairs[s].l_inf_diagonal();
			//std::cout << "src diagonal cost["<<s<<"] : " << edge_cost << std::endl;
		}
		else  {
			edge_cost = all_weights[std::pair<int,int>(s,src_matches[s])];
			std::cout << "src match cost["<<s<<"]["<<src_matches[s]<<"] : " << all_weights[std::pair<int,int>(s,src_matches[s])] << " -> " << our_pairs[s].l_inf_diagonal() << std::endl;
		}
		largest_cost = edge_cost > largest_cost ? edge_cost : largest_cost;
	}
	for(int d = 0; d < dst_matches.size(); d++)  {
		double edge_cost = -1;
		if(dst_matches[d] == -1)  {
			edge_cost = other_pairs[d].l_inf_diagonal();
			//std::cout << "dst diagonal cost["<<d<<"] : " << edge_cost << std::endl;
		}
		else  {
			edge_cost = all_weights[std::pair<int,int>(dst_matches[d],d)];
			//std::cout << "dst match cost["<<dst_matches[d]<<"]["<<d<<"] : " << all_weights[std::pair<int,int>(dst_matches[d],d)] << " -> " << other_pairs[d].l_inf_diagonal() << std::endl;
		}
		largest_cost = edge_cost > largest_cost ? edge_cost : largest_cost;
	}
	std::cout << "bottleneck distance: " << largest_cost << std::endl;

	return std::pair<std::vector<int>, std::vector<int> >(src_matches,dst_matches);
}

std::pair<std::vector<int>,std::vector<int> > PersistenceDiagram::wasserstein_matching(const PersistenceDiagram & _otherPD, int _d, double _p) const  {
	// construct matching matrix
	std::vector<PersistentPair> our_pairs = this->get_persistence_pairs(_d);
	std::vector<PersistentPair> other_pairs = _otherPD.get_persistence_pairs(_d);
	int max_size = our_pairs.size() + other_pairs.size();

	Eigen::MatrixXd cost_matrix = Eigen::MatrixXd::Zero(max_size,max_size);
	// connect all pairs of points
	for(int i = 0; i < our_pairs.size(); i++)  {
		PersistentPair our_pair = our_pairs[i];
		for(int j = 0; j < other_pairs.size(); j++)  {
			PersistentPair other_pair = other_pairs[j];
			cost_matrix(i,j) = pow(our_pair.l_inf_norm(other_pair),_p);
		}
	}
	// connect our pairs to diagonal
	for(int i = 0; i < our_pairs.size(); i++)  {
		PersistentPair our_pair = our_pairs[i];
		for(int j = other_pairs.size(); j < max_size; j++)
			cost_matrix(i,j) = pow(our_pair.l_inf_diagonal(),_p);
	}

	// connect other pairs to diagonal
	for(int j = 0; j < other_pairs.size(); j++)  {
		PersistentPair other_pair = other_pairs[j];
		for(int i = our_pairs.size(); i < max_size; i++) {
			cost_matrix(i,j) = pow(other_pair.l_inf_diagonal(),_p);
		}
	}

	// other method ...
	/*
	double** cost_mat = new double*[max_size];
	for(int i = 0; i < max_size; i++)  {
		cost_mat[i] = new double[max_size];
		for(int j = 0; j < max_size; j++)  {
			cost_mat[i][j] = cost_matrix(i,j);
		}
	}

	HungarianDistance hungarian(cost_mat,max_size,false);
	std::cout << "hungarian algorithm..." << std::endl;
	hungarian.compute();
	std::cout << "... done with hungarian algorithm..." << std::endl;

	for(int i = 0; i < max_size; i++)
		delete [] cost_mat[i];
	delete [] cost_mat;
	*/

	// weighted matching via Munkres method
	Munkres munkres;
	munkres.solve(cost_matrix);
	// perform assignment
	std::vector<int> our_assignment(our_pairs.size(),-2);
	std::vector<int> other_assignment(other_pairs.size(),-2);
	for(int i = 0; i < max_size; i++)  {
		for(int j = 0; j < max_size; j++)  {
			// no assignment
			if(cost_matrix(i,j) != 0)
				continue;

			// assignment made between i and j
			if(i < our_pairs.size() && j < other_pairs.size())  {
				our_assignment[i] = j;
				other_assignment[j] = i;
			}

			// assignment of i to diagonal
			else if(i < our_pairs.size())
				our_assignment[i] = -1;

			// assignment of j to diagonal
			else if(j < other_pairs.size())
				other_assignment[j] = -1;
		}
	}

	// verify: did we assign everyone?
	for(int i = 0; i < our_assignment.size(); i++)  {
		if(our_assignment[i] == -2)  {
			std::cout << "our not assigned!!! " << i << std::endl;
			our_assignment[i] = -1;
		}
	}
	for(int i = 0; i < other_assignment.size(); i++)  {
		if(other_assignment[i] == -2)  {
			std::cout << "other not assigned!!! " << i << std::endl;
			other_assignment[i] = -1;
		}
	}

	return std::pair<std::vector<int>, std::vector<int> >(our_assignment,other_assignment);
}

double PersistenceDiagram::wasserstein_distance(const PersistenceDiagram & _otherPD, int _d, double _p) const  {
	std::pair<std::vector<int>,std::vector<int> > matching = this->wasserstein_matching(_otherPD, _d, _p);
	std::vector<int> src_matchings = matching.first, dst_matchings = matching.second;
	double wasserstein_distance = 0;
	// compute src to dist pairings, including to the diagonal
	for(int s = 0; s < src_matchings.size(); s++)  {
		int s_pt = s, d_pt = src_matchings[s];
		PersistentPair s_pairing = this->get_pair(s_pt);
		if(d_pt == -1)  {
			wasserstein_distance += pow(s_pairing.l_inf_diagonal(),_p);
			continue;
		}
		PersistentPair d_pairing = _otherPD.get_pair(d_pt);
		wasserstein_distance += pow(s_pairing.l_inf_norm(d_pairing),_p);
	}
	int num_dst_diagonals = 0;
	for(int d = 0; d < dst_matchings.size(); d++)  {
		int d_pt = d, s_pt = dst_matchings[d];
		PersistentPair d_pairing = _otherPD.get_pair(d_pt);
		if(s_pt == -1)  {
			wasserstein_distance += pow(d_pairing.l_inf_diagonal(),_p);
			num_dst_diagonals++;
		}
	}
	return pow(wasserstein_distance,1/_p) / (src_matchings.size()+num_dst_diagonals);
	//return pow(wasserstein_distance,1/_p);
}

void PersistenceDiagram::write_to_file(std::string _filename, bool _writeGenerators)  {
	this->sort_pairs_by_persistence();
	FILE* file = fopen(_filename.c_str(), "w");
	for(int i = 0; i < all_pairs.size(); i++)  {
		PersistentPair pair = all_pairs[i];
		if(!_writeGenerators)  {
			fprintf(file, "%u %.7f %.7f\n", pair.dim(), pair.birth_time(), pair.death_time());
			continue;
		}
		fprintf(file, "%u %.7f %.7f", pair.dim(), pair.birth_time(), pair.death_time());
		for(int j = 0; j < pair.generator.size(); j++)
			fprintf(file, " %u", pair.generator[j]);
		fprintf(file, "\n");
	}
	fclose(file);
}
bool PersistenceDiagram::get_size_satisfied() { return this->_size_satisfied; }
