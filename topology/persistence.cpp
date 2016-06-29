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



#include "persistence.h"

PersistentHomology::PersistentHomology(bool _retainGenerators)  {
	retain_generators = _retainGenerators;
}

PersistentHomology::PersistentHomology(Filtration* _filtration, bool _retainGenerators)  {
	filtration = _filtration;
	max_d = filtration->maxD();
	retain_generators = _retainGenerators;
}

PersistentHomology::~PersistentHomology()  {
}


PersistenceDiagram *PersistentHomology::compute_persistence_sparse(SparseRipsFiltration* _filtration, int _maxD)  {
  max_d = _maxD;
  filtration = _filtration;
  // build filtration
  ComputationTimer filtration_timer("filtration computation time");
  filtration_timer.start();
  bool size_satisfied = filtration->build_filtration();
  filtration_timer.end();
  filtration_timer.dump_time();
  int filtration_size = filtration->filtration_size();
  std::cout << "total number of simplices: " << filtration_size << std::endl;

  // construct mapping between simplices and their identifiers -> only necessary for identifying simplex faces
  std::map<std::string,int> simplex_mapping;
  for(unsigned i = 0; i < filtration_size; i++)  {
    simplex_mapping[filtration->get_simplex(i).unique_unoriented_id()] = i+1;
  }

  // initialize reduction to boundaries - just a vector of lists
  PHCycle* reduction = new PHCycle[filtration_size+1];

  // initialize chains to identities
  PHCycle* chains = new PHCycle[filtration_size+1];

  // reserve 1st entry as dummy simplex, in line with reduced persistence
  reduction[0] = PHCycle();
  chains[0] = PHCycle();
  chains[0].push_back(0);
  // for each simplex, take its boundary and assign those simplices to its list
  for(unsigned i = 0; i < filtration_size; i++)  {
    int idx = i+1;
    reduction[idx] = PHCycle();
    chains[idx] = PHCycle();
    chains[idx].push_back(idx);
    Simplex simplex = filtration->get_simplex(i);
    // if 0-simplex, then reserve face as dummy simplex
    if(simplex.dim()==0)  {
      reduction[idx].push_back(0);
      continue;
    }

    std::vector<Simplex> faces = simplex.faces();
    for(unsigned f = 0; f < faces.size(); f++)  {
      Simplex next_face = faces[f];
      int face_id = simplex_mapping[next_face.unique_unoriented_id()];
      reduction[idx].push_back(face_id);
    }
    // sort list, so we can efficiently add cycles and inspect death cycles
    reduction[idx].sort();
  }
  simplex_mapping.clear();

  // initialize death cycle reference - nothing there yet, so just give it all -1
  int* death_cycle_ref = new int[filtration_size+1];
  for(unsigned i = 0; i < filtration_size+1; i++)
    death_cycle_ref[i] = -1;

  bool debug = false;
  std::cout << "doing the pairing..." << std::endl;
  std::vector< std::pair<int,int> > persistence_pairing;
  ComputationTimer persistence_timer("persistence computation time");
  persistence_timer.start();

  // perform pairing - but do so in decreasing simplex dimension
  //for(int d = max_d; d >= 0; d--)  {
  for(int d = 0; d <= max_d; d++)  {
    for(unsigned i = 0; i < filtration_size; i++)  {
      if(filtration->get_simplex(i).dim() != d)
	continue;
      int idx = i+1;
      double simplex_distance = filtration->get_simplex(i).get_simplex_distance();

      // until we are either definitively a birth cycle or a death cycle ...
      int low_i = reduction[idx].back();
      if(debug) std::cout << "start reduction["<<idx<<"] size: " << reduction[idx].size() << std::endl;
      int num_chains_added = 0;
      while(reduction[idx].size() > 0 && death_cycle_ref[low_i] != -1)  {
	num_chains_added++;
	// add the prior death cycle to us
	int death_cycle_ind = death_cycle_ref[low_i];

	PHCycle::iterator our_cycle_iter = reduction[idx].begin(), added_cycle_iter = reduction[death_cycle_ind].begin();
	while(added_cycle_iter != reduction[death_cycle_ind].end())  {
	  if(our_cycle_iter == reduction[idx].end())  {
	    reduction[idx].push_back(*added_cycle_iter);
	    ++added_cycle_iter;
	    continue;
	  }
	  int sigma_1 = *our_cycle_iter, sigma_2 = *added_cycle_iter;
	  if(sigma_1 == sigma_2)  {
	    our_cycle_iter = reduction[idx].erase(our_cycle_iter);
	    ++added_cycle_iter;
	  }
	  else if(sigma_1 < sigma_2)
	    ++our_cycle_iter;
	  else  {
	    reduction[idx].insert(our_cycle_iter, sigma_2);
	    ++added_cycle_iter;
	  }
	}
	if(retain_generators && d != max_d)
	  chains[idx].push_back(death_cycle_ind);

	/*
                                reduction[idx] = this->merge_cycles(reduction[idx], reduction[death_cycle_ind]);
	*/
	if(debug) std::cout << "reduction["<<idx<<"] size: " << reduction[idx].size() << " | " << reduction[death_cycle_ind].size() << std::endl;
	low_i = reduction[idx].back();
      }

      // if we are a death cycle then add us to the list, add as persistence pairings
      if(reduction[idx].size() > 0)  {
	//std::cout << "death cycle ["<<idx<<"]" << " : " << simplex_distance << " -> " << num_chains_added << std::endl;
	death_cycle_ref[low_i] = idx;
	// kill cycle at low_i, since it represents a birth
	reduction[low_i] = PHCycle();
	if(low_i > 0)
	  persistence_pairing.push_back(std::pair<int,int>(low_i-1,idx-1));
      }
      //else
      //      std::cout << "chain size["<<idx<<"]: " << chains[idx].size() << " : " << simplex_distance << " -> " << num_chains_added << std::endl;
    }
  }
  persistence_timer.end();
  persistence_timer.dump_time();

  delete [] death_cycle_ref;

  std::vector<PersistentPair> persistent_pairs;
  for(unsigned i = 0; i < persistence_pairing.size(); i++)  {
    std::pair<int,int> pairing = persistence_pairing[i];
    Simplex birth_simplex = filtration->get_simplex(pairing.first), death_simplex = filtration->get_simplex(pairing.second);
    if(death_simplex.get_simplex_distance() == birth_simplex.get_simplex_distance())
      continue;

    PersistentPair persistent_pair(birth_simplex.dim(), birth_simplex.get_simplex_distance(), death_simplex.get_simplex_distance());
    Simplex first_simplex = filtration->get_simplex(pairing.first);
    int simplex_dim = first_simplex.dim();

    if(retain_generators)  {
      std::list<int> generating_cycle = this->expand_chain(pairing.first+1,chains);
      std::map<int,int> simplex_counts;
      for(std::list<int>::iterator chain_iter = generating_cycle.begin(); chain_iter != generating_cycle.end(); ++chain_iter)
	simplex_counts[(*chain_iter-1)] = simplex_counts[(*chain_iter-1)]+1;

      std::map<int,int> vertex_counts;
      //std::cout << "generator for simplex["<<birth_simplex.dim()<<"] " << (pairing.first+1) << " {";
      for(std::list<int>::iterator chain_iter = generating_cycle.begin(); chain_iter != generating_cycle.end(); ++chain_iter)  {
	Simplex generating_simplex = filtration->get_simplex(*chain_iter-1);
	if(generating_simplex.dim() != simplex_dim)
	  std::cout << "simplex dimensionality mismatch!" << simplex_dim << " : " << generating_simplex.dim() << std::endl;

	if(simplex_counts[(*chain_iter-1)] % 2 == 0)
	  continue;

	for(int v = 0; v <= generating_simplex.dim(); v++)  {
	  int vertex = generating_simplex.vertex(v);
	  persistent_pair.add_generator_pt(vertex);
	  if(vertex_counts.find(vertex) == vertex_counts.end())
	    vertex_counts[vertex] = 1;
	  else
	    vertex_counts[vertex] = vertex_counts[vertex]==0 ? 1 : 0;
	}
      }

      if(simplex_dim > 0)  {
	bool is_cycle = true;
	for(std::map<int,int>::iterator simplex_iter = vertex_counts.begin(); simplex_iter != vertex_counts.end(); ++simplex_iter)  {
	  int simplex = simplex_iter->first, counts = simplex_iter->second;
	  if(counts != 0)  {
	    is_cycle = false;
	    std::cout << "not a cycle! partly due to " << simplex << std::endl;
	  }
	}

	if(!is_cycle)  {
	  std::cout << "["<<simplex_dim<<"] {";
	  for(int v = 0; v < persistent_pair.generator_size(); v++)
	    std::cout << " " << persistent_pair.get_generator_pt(v);
	  std::cout << " }" << std::endl;
	}
      }
    }

    persistent_pairs.push_back(persistent_pair);
  }

  delete [] chains;
  delete [] reduction;

  PersistenceDiagram *pd = new PersistenceDiagram(persistent_pairs);
  pd->size_satisfied(size_satisfied);
  return pd;
}

PersistenceDiagram *PersistentHomology::compute_persistence_full(RipsFiltration* _filtration, int _maxD)  {
  filtration = _filtration;
  max_d = _maxD;
  // build filtration
  ComputationTimer filtration_timer("filtration computation time");
  filtration_timer.start();
  filtration->build_filtration();
  filtration_timer.end();
  filtration_timer.dump_time();
  int filtration_size = filtration->filtration_size();
  std::cout << "total number of simplices: " << filtration_size << std::endl;

  // construct mapping between simplices and their identifiers -> only necessary for identifying simplex faces
  std::map<std::string,int> simplex_mapping;
  for(unsigned i = 0; i < filtration_size; i++)  {
    simplex_mapping[filtration->get_simplex(i).unique_unoriented_id()] = i+1;
  }

  // initialize reduction to boundaries - just a vector of lists
  PHCycle* reduction = new PHCycle[filtration_size+1];

  // reserve 1st entry as dummy simplex, in line with reduced persistence
  reduction[0] = PHCycle();
  // for each simplex, take its boundary and assign those simplices to its list
  for(unsigned i = 0; i < filtration_size; i++)  {
    int idx = i+1;
    reduction[idx] = PHCycle();
    Simplex simplex = filtration->get_simplex(i);
    // if 0-simplex, then reserve face as dummy simplex
    if(simplex.dim()==0)  {
      reduction[idx].push_back(0);
      continue;
    }

    std::vector<Simplex> faces = simplex.faces();
    for(unsigned f = 0; f < faces.size(); f++)  {
      Simplex next_face = faces[f];
      int face_id = simplex_mapping[next_face.unique_unoriented_id()];
      reduction[idx].push_back(face_id);
    }
    // sort list, so we can efficiently add cycles and inspect death cycles
    reduction[idx].sort();
  }
  simplex_mapping.clear();

  // initialize death cycle reference - nothing there yet, so just give it all -1
  int* death_cycle_ref = new int[filtration_size+1];
  for(unsigned i = 0; i < filtration_size+1; i++)
    death_cycle_ref[i] = -1;

  bool debug = false;
  std::cout << "doing the pairing..." << std::endl;
  std::vector< std::pair<int,int> > persistence_pairing;
  ComputationTimer persistence_timer("persistence computation time");
  persistence_timer.start();
  // perform pairing - but do so in decreasing simplex dimension
  for(int d = max_d; d >= 0; d--)  {
    for(unsigned i = 0; i < filtration_size; i++)  {
      if(filtration->get_simplex(i).dim() != d)
	continue;
      int idx = i+1;

      // until we are either definitively a birth cycle or a death cycle ...
      int low_i = reduction[idx].back();
      if(debug) std::cout << "start reduction["<<idx<<"] size: " << reduction[idx].size() << std::endl;
      while(reduction[idx].size() > 0 && death_cycle_ref[low_i] != -1)  {
	// add the prior death cycle to us
	int death_cycle_ind = death_cycle_ref[low_i];

	PHCycle::iterator our_cycle_iter = reduction[idx].begin(), added_cycle_iter = reduction[death_cycle_ind].begin();
	while(added_cycle_iter != reduction[death_cycle_ind].end())  {
	  if(our_cycle_iter == reduction[idx].end())  {
	    reduction[idx].push_back(*added_cycle_iter);
	    ++added_cycle_iter;
	    continue;
	  }
	  int sigma_1 = *our_cycle_iter, sigma_2 = *added_cycle_iter;
	  if(sigma_1 == sigma_2)  {
	    our_cycle_iter = reduction[idx].erase(our_cycle_iter);
	    ++added_cycle_iter;
	  }
	  else if(sigma_1 < sigma_2)
	    ++our_cycle_iter;
	  else  {
	    reduction[idx].insert(our_cycle_iter, sigma_2);
	    ++added_cycle_iter;
	  }
	}

	/*
                                reduction[idx] = this->merge_cycles(reduction[idx], reduction[death_cycle_ind]);
	*/
	if(debug) std::cout << "reduction["<<idx<<"] size: " << reduction[idx].size() << " | " << reduction[death_cycle_ind].size() << std::endl;
	low_i = reduction[idx].back();
      }

      // if we are a death cycle then add us to the list, add as persistence pairings
      if(reduction[idx].size() > 0)  {
	death_cycle_ref[low_i] = idx;
	// kill cycle at low_i, since it represents a birth
	reduction[low_i] = PHCycle();
	if(low_i > 0)
	  persistence_pairing.push_back(std::pair<int,int>(low_i-1,idx-1));
      }
    }
  }
  persistence_timer.end();
  persistence_timer.dump_time();

  delete [] death_cycle_ref;

  std::vector<PersistentPair> persistent_pairs;;
  for(unsigned i = 0; i < persistence_pairing.size(); i++)  {
    std::pair<int,int> pairing = persistence_pairing[i];
    Simplex birth_simplex = filtration->get_simplex(pairing.first), death_simplex = filtration->get_simplex(pairing.second);
    //std::cout << "birth simplex time: " << birth_simplex.get_simplex_distance() << " ; death simplex time: " << death_simplex.get_simplex_distance() << std::endl;
    if(death_simplex.get_simplex_distance() == birth_simplex.get_simplex_distance())
      continue;
    persistent_pairs.push_back(PersistentPair(birth_simplex.dim(), birth_simplex.get_simplex_distance(), death_simplex.get_simplex_distance()));
  }

  delete [] reduction;

  return new PersistenceDiagram(persistent_pairs);
}


PHCycle PersistentHomology::merge_cycles(const PHCycle & _c1, const PHCycle & _c2)  {
	PHCycle merged_cycle;
	PHCycle::const_iterator c1_iter = _c1.begin(), c2_iter = _c2.begin();
	while(c1_iter != _c1.end() || c2_iter != _c2.end())  {
		if(c1_iter == _c1.end())  {
			merged_cycle.push_back(*c1_iter);
			++c1_iter;
		}
		else if(c2_iter == _c2.end())  {
			merged_cycle.push_back(*c2_iter);
			++c2_iter;
		}
		else  {
			int sigma_1 = *c1_iter, sigma_2 = *c2_iter;
			if(sigma_1 == sigma_2)  {
				++c1_iter;
				++c2_iter;
			}
			else if(sigma_1 < sigma_2)  {
				merged_cycle.push_back(sigma_1);
				++c1_iter;
			}
			else  {
				merged_cycle.push_back(sigma_2);
				++c2_iter;
			}
		}
	}
	return merged_cycle;
}

std::list<int> PersistentHomology::expand_chain(int _chain, PHCycle* _allChains)  {
	std::list<int> expanded_chain;
	for(std::list<int>::iterator chain_iter = _allChains[_chain].begin(); chain_iter != _allChains[_chain].end(); ++chain_iter)  {
		if(*chain_iter == _chain)
			expanded_chain.push_back(_chain);
		else  {
			std::list<int> sub_chain = this->expand_chain(*chain_iter, _allChains);
			for(std::list<int>::iterator sub_chain_iter = sub_chain.begin(); sub_chain_iter != sub_chain.end(); ++sub_chain_iter)
				expanded_chain.push_back(*sub_chain_iter);
		}
	}
	return expanded_chain;
}
