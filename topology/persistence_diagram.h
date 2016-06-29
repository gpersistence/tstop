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



#ifndef PERSISTENCEDIAGRAM_H
#define PERSISTENCEDIAGRAM_H

#include <Eigen/Dense>
#include <vector>
#include <map>

#include <boost/compressed_pair.hpp>
#include <boost/optional.hpp>
#include <boost/serialization/access.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/nvp.hpp>

#include <boost/iterator/counting_iterator.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/max_cardinality_matching.hpp>

#include "../geometry/point_incs.h"
#include "munkres/munkres.h"
#include "munkres/HungarianDistance.h"

struct PersistentPair  {
	PersistentPair() : d(0), birth(0), death(0)  {}
	PersistentPair(int _d, double _birth, double _death) : d(_d), birth(_birth), death(_death)  {}

	int dim() const { return d; }
	double birth_time() const { return birth; }
	double death_time() const { return death; }
	double persistence() const { return death-birth; }

	double l_inf_norm(const PersistentPair& _otherPair) const {
		return std::max(std::abs(birth-_otherPair.birth), std::abs(death-_otherPair.death));
	}

	double l_inf_diagonal() const {
		return (death-birth)/2;
	}

	inline bool operator<(const PersistentPair& _simp) const {
		if(d < _simp.dim())
			return true;
		else if(_simp.dim() < d)
			return false;
		return this->persistence() < _simp.persistence();
	}

	int generator_size()  { return generator.size(); }
	int get_generator_pt(int _i)  { return generator[_i]; }
	void add_generator_pt(int _i)  { generator.push_back(_i); }

	int d;
	double birth, death;
	std::vector<int> generator;
};

struct WeightedEdge : public std::pair<unsigned, unsigned>  {
	typedef std::pair<unsigned, unsigned>                       Parent;
	WeightedEdge(unsigned v1, unsigned v2, double d): Parent(v1,v2), distance(d)  {}
	bool operator<(const WeightedEdge& other) const { return distance < other.distance; }
	double distance;
};

typedef std::vector<WeightedEdge> EdgeVector;
typedef EdgeVector::const_iterator EV_const_iterator;
typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS> Graph;
typedef std::vector<boost::graph_traits<Graph>::vertex_descriptor> MatchingVector;

struct CardinalityComparison  {

	CardinalityComparison(unsigned size, EV_const_iterator begin) : max_size(size), bg(begin), last(bg), g(2*max_size), mates(2*max_size)  {
		boost::add_edge(bg->first, bg->second, g);
	}

	bool operator()(EV_const_iterator i1, EV_const_iterator i2)  {
		//std::cout << "trying ("<<i1->first << ","<<i1->second << ") : " << i1->distance << " ; ("<<i2->first << ","<<i2->second << ") : " << i2->distance << std::endl;
		if (i2 > last)  {
			do  {
				++last;
				//std::cout << "adding edge " << last->first << " , " << last->second << " -> " << last->distance << std::endl;
				boost::add_edge(last->first, last->second, g);
			} while (last != i2);
		}
		else  {
			do  {
				//std::cout << "removing edge " << last->first << " , " << last->second << " -> " << last->distance << std::endl;
				boost::remove_edge(last->first, last->second, g);
			} while (--last != i2);
		}
		edmonds_maximum_cardinality_matching(g, &mates[0]);
		/*
		for(int m = 0; m < mates.size(); m++)  {
			std::cout << "match["<<m<<"] -> " << mates[m] << std::endl;
		}
		*/
		//std::cout << "at the matching size? " << (matching_size(g, &mates[0]) == max_size) << std::endl;
		return matching_size(g, &mates[0]) == max_size;
	}

    unsigned max_size;
    EV_const_iterator bg;
    EV_const_iterator last;
    Graph g;
    MatchingVector mates;
};

class PersistenceDiagram  {
	public:
		PersistenceDiagram()  {}
		PersistenceDiagram(std::string _filename);
		PersistenceDiagram(const std::vector<PersistentPair> & _allPairs);
		~PersistenceDiagram();

		double bottleneck_distance(const PersistenceDiagram & _otherPD, int _d) const;
		std::pair<std::vector<int>,std::vector<int> > bottleneck_matcher(const PersistenceDiagram & _otherPD, int _d) const;
		std::pair<std::vector<int>,std::vector<int> > wasserstein_matching(const PersistenceDiagram & _otherPD, int _d, double _p=1) const;
		double wasserstein_distance(const PersistenceDiagram & _otherPD, int _d, double _p=1) const;

		int num_pairs() const { return all_pairs.size(); }
		PersistentPair get_pair(int _i) const { return all_pairs[_i]; }

		int max_d() const  {
			int max_d = 0;
			for(int i = 0; i < all_pairs.size(); i++)  {
				int next_d = all_pairs[i].d;
				max_d = next_d > max_d ? next_d : max_d;
			}
			return max_d;
		}

		std::vector<PersistentPair> get_persistence_pairs(int _d) const {
			std::vector<PersistentPair> persistence_pairs;
			for(unsigned i = 0; i < all_pairs.size(); i++)  {
				PersistentPair pair = all_pairs[i];
				if(pair.d == _d)
					persistence_pairs.push_back(pair);
			}
			return persistence_pairs;
		}

		double maximum_persistence(int _d) const  {
			double max_persistence = 0;
			for(unsigned i = 0; i < all_pairs.size(); i++)  {
				PersistentPair pair = all_pairs[i];
				if(pair.d != _d)
					continue;
				max_persistence = pair.persistence() > max_persistence ? pair.persistence() : max_persistence;
			}
			return max_persistence;
		}

		void sort_pairs_by_persistence()  {
			std::sort(all_pairs.begin(),all_pairs.end());
		}

		void write_to_file(std::string _filename, bool _writeGenerators=false);

		bool get_size_satisfied();
		void size_satisfied(bool in) { this->_size_satisfied = in; }
	private:
		std::vector<PersistentPair> all_pairs;
		  bool _size_satisfied;
};

struct LabeledPersistenceDiagram  {
	LabeledPersistenceDiagram(PersistenceDiagram _pd, int _label) : pd(_pd), label(_label)  {}
	PersistenceDiagram pd;
	int label;
};

#endif
