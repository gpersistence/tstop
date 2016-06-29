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



#include "covertree.h"

CoverTree::CoverTree(const SparsePoints & _points, double _scale)  {
	debug = false;

	points = _points;
	scale = _scale;

	diameter_ub = 0;
	//center = SparseVector(points[0].dim());
	for(int i = 1; i < points.size(); i++)  {
		SparseVector p_i = points[i];
		//center = center + p_i;
		for(int j = 0; j < i; j++)  {
			SparseVector p_j = points[j];
			double dist = p_i.length(p_j);
			diameter_ub = dist > diameter_ub ? dist : diameter_ub;
		}
	}
	//center = center*(1.0/points.size());

	is_constructed = false;
	root_level = (int)(log(diameter_ub)/log(scale))+1;
	std::cout << "diameter: " << diameter_ub << " ; quantized upper bound: " << pow(scale,root_level) << " root level: " << root_level << std::endl;
}

CoverTree::CoverTree(const SparsePoints & _points, std::vector<int> _levels, std::vector<int> _parents, double _scale)  {
	debug = false;

	points = _points;
	scale = _scale;

	// find max and min levels
	root_level = -10000;
	int min_level = 10000;
	for(int i = 0; i < _levels.size(); i++)  {
		root_level = _levels[i] > root_level ? _levels[i] : root_level;
		min_level = _levels[i] < min_level ? _levels[i] : min_level;
	}

	diameter_ub = 0;
	//center = SparseVector(points[0].dim());
	for(int i = 1; i < points.size(); i++)  {
		SparseVector p_i = points[i];
		//center = center + p_i;
		for(int j = 0; j < i; j++)  {
			SparseVector p_j = points[j];
			double dist = p_i.length(p_j);
			diameter_ub = dist > diameter_ub ? dist : diameter_ub;
		}
	}
	//center = center*(1.0/points.size());

	std::cout << "diameter: " << diameter_ub << " ; quantized upper bound: " << pow(scale,root_level) << " root level: " << root_level << std::endl;

	/*
	for(int i = 0; i < _levels.size(); i++)  {
		if(_levels[i] == root_level)  {
			root_node = new CoverTreeNode(i,_levels[i]);
			break;
		}
	}
	for(int i = 0; i < _levels.size(); i++)  {
		if(_levels[i] != root_level)  {
			std::cout << "creating and inserting " << i << " : " << _levels[i] << " : " << _parents[i] << std::endl;
			root_node->create_and_insert_node(i,_levels[i],_parents[i]);
		}
	}
	*/

	for(int l = root_level; l >= min_level; l--)  {
		for(int i = 0; i < _levels.size(); i++)  {
			if(_levels[i] != l)
				continue;
			if(_levels[i] == root_level)  {
				root_node = new CoverTreeNode(i,_levels[i]);
				continue;
			}
			if(debug) std::cout << "creating and inserting " << i << " : " << _levels[i] << " : " << _parents[i] << std::endl;
			root_node->create_and_insert_node(i,_levels[i],_parents[i]);
		}
	}

	check_invariants();

	std::vector<double> node_radii = std::vector<double>(points.size(),0);
	parent_radii = std::vector<double>(points.size(),0);
	root_node->populate_parent_radii(&node_radii,&parent_radii,points,scale);
	if(debug)  {
		for(int i = 0; i < parent_radii.size(); i++)
			std::cout << "parent radii["<<i<<"] : " << parent_radii[i] << std::endl;
	}
	is_constructed = true;
}

CoverTree::~CoverTree()  {
	if(is_constructed)  {
		std::cout << "deleting root node..." << std::endl;
		delete root_node;
	}
	std::cout << "... done deleting cover tree..." << std::endl;
}

std::set<int> CoverTree::ball_query(SparseVector _pt, double _radius)  {
	std::vector<CoverTreeNode*> cover_set;
	cover_set.push_back(root_node);
	bool all_leaves = false;

	while(!all_leaves && cover_set.size() > 0)  {
		double this_level = cover_set[0]->level();
		double scale_bound = pow(scale,this_level);
		std::vector<CoverTreeNode*> children_candidates;
		for(int s = 0; s < cover_set.size(); s++)  {
			CoverTreeNode* node = cover_set[s];
			std::vector<CoverTreeNode*> children = node->get_children();
			for(int c = 0; c < children.size(); c++)
				children_candidates.push_back(children[c]);
		}

		cover_set.clear();
		all_leaves = true;
		for(int c = 0; c < children_candidates.size(); c++)  {
			CoverTreeNode* next_node = children_candidates[c];
			if(!next_node->is_leaf())
				all_leaves = false;
			if(_pt.length(points[next_node->idx()]) <= (_radius+scale*scale_bound))
				cover_set.push_back(next_node);
		}
	}

	std::set<int> neighbors;
	for(int c = 0; c < cover_set.size(); c++)  {
		CoverTreeNode* node = cover_set[c];
		if(_pt.length(points[node->idx()]) <= _radius)
			neighbors.insert(node->idx());
	}

	//std::cout << "neighbors found " << neighbors.size() << " / " << cover_set.size() << std::endl;

	return neighbors;
}

void CoverTree::build_tree()  {
	// randomize insertion
	std::vector<int> permutation, original_inds;
	for(int i = 0; i < points.size(); i++)
		original_inds.push_back(i);
	for(int i = 0; i < points.size(); i++)  {
		int rand_ind = rand() % (points.size()-i);
		int rand_val = original_inds[rand_ind];
		permutation.push_back(rand_val);
		//permutation.push_back(i);
		original_inds[rand_ind] = original_inds[points.size()-i-1];
	}
	permutation = this->fps();

	int num_insertions = 0;
	for(int i = 0; i < permutation.size(); i++)  {
		if(debug) std::cout << "inserting point " << permutation[i] << " ... " << std::endl;
		int inserted_level = this->insert_point(permutation[i]);
		if(inserted_level != (root_level+1))
			num_insertions++;
	}

	if(debug) std::cout << "num insertions: " << num_insertions << std::endl;
	check_invariants();

	std::vector<double> node_radii = std::vector<double>(points.size(),0);
	parent_radii = std::vector<double>(points.size(),0);
	root_node->populate_parent_radii(&node_radii,&parent_radii,points,scale);
	if(debug)  {
		for(int i = 0; i < parent_radii.size(); i++)
			std::cout << "parent radii["<<i<<"] : " << parent_radii[i] << std::endl;
	}
}

int CoverTree::insert_point(int _i)  {
	if(!is_constructed)  {
		root_node = new CoverTreeNode(_i, root_level);
		is_constructed = true;
		return root_level;
	}

	std::vector<CoverTreeNode*> root_candidate;
	root_candidate.push_back(root_node);
	int inserted_level;
	if(this->insert_point(_i, root_candidate, root_level, inserted_level))
		return inserted_level;
	else
		return root_level+1;
}

double CoverTree::distance_to_set(int _q, const std::vector<CoverTreeNode*> & _nodes)  {
	SparseVector p_q = points[_q];
	double dist = -1;
	for(int c = 0; c < _nodes.size(); c++)  {
		CoverTreeNode* node = _nodes[c];
		SparseVector p_c = points[node->idx()];
		double next_dist = p_q.length(p_c);
		if(dist == -1)
			dist = next_dist;
		else
			dist = next_dist < dist ? next_dist : dist;
	}
	return dist;
}

bool CoverTree::insert_point(int _q, const std::vector<CoverTreeNode*> & _coverSet, int _l, int & inserted_level)  {
	if(debug) std::cout << "point insertion for level " << _l << std::endl;
	double cover_bound = pow(scale,_l);
	// gather all children associated with the candidate parents
	std::vector<CoverTreeNode*> children_of_candidates;
	for(int p = 0; p < _coverSet.size(); p++)  {
		CoverTreeNode* candidate_node = _coverSet[p];
		std::vector<CoverTreeNode*> children_of_candidate = candidate_node->get_children();
		for(int c = 0; c < children_of_candidate.size(); c++)
			children_of_candidates.push_back(children_of_candidate[c]);
	}

	// separation criterion
	SparseVector p_q = points[_q];
	double candidate_set_distance = this->distance_to_set(_q, children_of_candidates);
	if(candidate_set_distance == 0)  {
		std::cout << "duplicate point!" << std::endl;
		inserted_level = root_level+1;
		return false;
	}
	if(candidate_set_distance > cover_bound)  {
		//std::cout << "no parent found! " << _l << std::endl;
		return false;
	}
	//else
	//	std::cout << "candidate set distance: " << candidate_set_distance << std::endl;

	std::vector<CoverTreeNode*> child_cover_set;
	for(int p = 0; p < children_of_candidates.size(); p++)  {
		CoverTreeNode* child_node = children_of_candidates[p];
		if(p_q.length(points[child_node->idx()]) <= cover_bound)
			child_cover_set.push_back(child_node);
	}

	double cover_set_distance = this->distance_to_set(_q, _coverSet);
	if(cover_set_distance == -1)
		std::cout << "... empty cover set?" << std::endl;
	bool is_parent_found = this->insert_point(_q, child_cover_set, _l-1, inserted_level);
	if(!is_parent_found && cover_set_distance > cover_bound)  {
		if(debug) std::cout << "parent not found, but cover set distance not satisifed" << std::endl;
		return false;
	}
	if(!is_parent_found && cover_set_distance <= cover_bound)  {
		if(inserted_level == (root_level+1))
			return false;
		CoverTreeNode* parent;
		int num_potential_parents = 0;
		double min_dist = -1;
		for(int i = 0; i < _coverSet.size(); i++)  {
			CoverTreeNode* node = _coverSet[i];
			double dist = p_q.length(points[node->idx()]);
			//if(dist < cover_bound && node->fully_covers(p_q, points, scale))  {
			if(p_q.length(points[node->idx()]) <= cover_bound)  {
				if(min_dist == -1 || dist < min_dist)  {
					parent = node;
					min_dist = dist;
				}
				num_potential_parents++;
				//break;
			}
		}
		if(min_dist == -1)
			std::cout << "no parent found!!!" << std::endl;
		inserted_level = _l-1;
		if(debug) std::cout << "inserting child at level " << _l-1 << " ... out of " << num_potential_parents << " potential parents" << std::endl;
		parent->insert_child(new CoverTreeNode(parent,_q,_l-1));
		return true;
	}
	else  {
		//std::cout << "no insertion?" << std::endl;
		return true;
	}
}

void CoverTree::check_invariants()  {
	std::vector<CoverTreeNode*> all_nodes;
	std::set<int> unique_ids;
	root_node->get_unique_nodes(&all_nodes, &unique_ids);
	std::cout << "number of unique nodes: " << all_nodes.size() << std::endl;

	// invariant 1: nesting
	for(int i = 0; i < all_nodes.size(); i++)  {
		CoverTreeNode* node = all_nodes[i];
		bool found_child = false;
		while(!found_child)  {
			if(node->is_leaf())  {
				found_child = true;
				break;
			}

			bool found_itself = false;
			std::vector<CoverTreeNode*> children = node->get_children();
			for(int j = 0; j < children.size(); j++)  {
				CoverTreeNode* child_node = children[j];
				if(child_node->idx() == node->idx())  {
					node = child_node;
					found_itself = true;
					break;
				}
			}

			if(!found_itself)
				std::cout << "nesting violated!" << std::endl;
		}
	}

	// invariant 2: covering
	for(int i = 0; i < all_nodes.size(); i++)  {
		CoverTreeNode* node = all_nodes[i];
		if(node->is_root())
			continue;
		CoverTreeNode* parent_node = node->get_parent();
		double parent_radius = pow(scale,parent_node->level());
		if(points[node->idx()].length(points[parent_node->idx()]) >= parent_radius)
			std::cout << "covering violation! " << parent_radius << " : " << points[node->idx()].length(points[parent_node->idx()]) << std::endl;
	}

	// invariant 3: separation
	double packing_quality = 0;
	double packing_weight = 0;
	for(int i = 1; i < all_nodes.size(); i++)  {
		CoverTreeNode* node_i = all_nodes[i];
		for(int j = 0; j < i; j++)  {
			CoverTreeNode* node_j = all_nodes[j];
			if(node_i->level() != node_j->level())
				continue;
			double dist_check = pow(scale,node_i->level());
			if(points[node_i->idx()].length(points[node_j->idx()]) <= dist_check)
				std::cout << "separation violation! " << points[node_i->idx()].length(points[node_j->idx()]) << " : " << dist_check << std::endl;
			else  {
				packing_quality += points[node_i->idx()].length(points[node_j->idx()])/dist_check;
				packing_weight++;
			}
			//else
			//	std::cout << "packing quality["<<node_i->level()<<"]: " << points[node_i->idx()].length(points[node_j->idx()]) << " : " << dist_check << std::endl;
		}
	}
	std::cout << "packing quality: " << packing_quality/packing_weight << std::endl;

	// are all children at a given node covered?
	for(int i = 0; i < all_nodes.size(); i++)  {
		CoverTreeNode* node = all_nodes[i];
		std::vector<CoverTreeNode*> all_children;
		node->get_all_child_nodes(&all_children);
		double main_radius = pow(scale,node->level());
		for(int c = 0; c < all_children.size(); c++)  {
			CoverTreeNode* child_node = all_children[c];
			/*
			if(points[node->idx()].length(points[child_node->idx()]) >= main_radius)
				std::cout << "subtree covering violation["<<node->level()<<"] : ["<<node->idx()<<"]["<<child_node->idx()<<"] : " << points[node->idx()].length(points[child_node->idx()]) << " : " << main_radius << " -> " << child_node->level() << std::endl;
				*/
		}
	}
}

std::vector<int> CoverTree::fps()  {
	std::vector<int> sampling;
	/*
	int closest_center_ind = -1;
	double closest_center_dist = -1;
	for(int i = 0; i < points.size(); i++)  {
		SparseVector pt = points[i];
		double dist = pt.length(center);
		if(closest_center_ind == -1 || dist < closest_center_dist)  {
			closest_center_dist = dist;
			closest_center_ind = i;
		}
	}
	sampling.push_back(closest_center_ind);
	*/
	sampling.push_back(0);

	double* minimum_distances = new double[points.size()];
	for(int i = 0; i < points.size(); i++)  {
		unsigned fp = sampling[0];
		minimum_distances[i] = points[fp].sqd_dist(points[i]);
	}

	// add points one at a time, farthest in Euclidean distance from all other points
	std::cout << "farthest point sampling " << std::flush;
	int num_dots = 50 >= points.size() ? (points.size()-1) : 50;
	int dot_interval = points.size() / num_dots;
	for(int i = 1; i < points.size(); i++)  {
		if(i % dot_interval == 0)
			std::cout << "." << std::flush;
		double max_dist = -1e10;
		int best_ind = -1;

		// find minimum distance to all farthest points
		for(int p = 0; p < points.size(); p++)  {
			if(minimum_distances[p] > max_dist)  {
				max_dist = minimum_distances[p];
				best_ind = p;
			}
		}

		// update minimum distances with newly added point
		for(int j = 0; j < points.size(); j++)  {
			double new_dist = points[best_ind].sqd_dist(points[j]);
			minimum_distances[j] = new_dist < minimum_distances[j] ? new_dist : minimum_distances[j];
		}
		sampling.push_back(best_ind);
	}
	std::cout << std::endl;
	delete [] minimum_distances;

	return sampling;
}

CoverTreeNode::CoverTreeNode(CoverTreeNode* _parent, int _i, int _l)  {
	parent = _parent;
	has_parent = true;
	i = _i;
	l = _l;
}

CoverTreeNode::CoverTreeNode(int _i, int _l)  {
	has_parent = false;
	i = _i;
	l = _l;
}

CoverTreeNode::~CoverTreeNode()  {
	/*
	std::cout << "deleting cover tree node " << i << std::endl;
	for(int c = 0; c < children.size(); c++)
		delete children[c];
	std::cout << "... done deleting cover tree node " << i << std::endl;
	*/
}

std::vector<CoverTreeNode*> CoverTreeNode::get_children()  {
	if(children.size() == 0)
		children.push_back(new CoverTreeNode(this, i, l-1));
	return children;
}

void CoverTreeNode::get_unique_nodes(std::vector<CoverTreeNode*>* nodes, std::set<int>* unique_ids)  {
	if(unique_ids->find(i) == unique_ids->end())  {
		unique_ids->insert(i);
		nodes->push_back(this);
	}
	for(int c = 0; c < children.size(); c++)
		children[c]->get_unique_nodes(nodes, unique_ids);
}

void CoverTreeNode::get_all_child_nodes(std::vector<CoverTreeNode*>* nodes)  {
	for(int c = 0; c < children.size(); c++)
		nodes->push_back(children[c]);
	for(int c = 0; c < children.size(); c++)
		children[c]->get_all_child_nodes(nodes);
}

void CoverTreeNode::populate_parent_radii(std::vector<double>* node_radii, std::vector<double>* parent_radii, const SparsePoints & _points, double _scale)  {
	if(!this->is_leaf() && node_radii->at(i) == 0)  {
		double max_dist = -1;
		for(int c = 0; c < children.size(); c++)  {
			SparseVector c_pt = _points[children[c]->i];
			double distance = _points[i].length(c_pt);
			max_dist = distance > max_dist ? distance : max_dist;
		}
		/*
		if(max_dist == 0)
			std::cout << "zero node radii? " << l << " -> " << children.size() << std::endl;
		else
			std::cout << "nonzero node radii " << l << " -> " << children.size() << std::endl;
			*/
		(*node_radii)[i] = max_dist;
	}

	if(parent_radii->at(i) == 0)  {
		if(this->is_root())  {
			(*parent_radii)[i] = pow(_scale,l+1);
		}
		else  {
			//std::cout << "setting up intermediate node... " << node_radii->at(parent->i) << std::endl;
			if(node_radii->at(parent->i) == 0)
				(*parent_radii)[i] = pow(_scale,l+1);
			else  {
				//std::cout << "nonzero parent radii: " << node_radii->at(parent->i) << std::endl;
				(*parent_radii)[i] = node_radii->at(parent->i);
			}
		}

		if(true)  {
			(*parent_radii)[i] = pow(_scale,l+1);
		}
	}
	for(int c = 0; c < children.size(); c++)
		children[c]->populate_parent_radii(node_radii,parent_radii,_points,_scale);
}

bool CoverTreeNode::fully_covers(const SparseVector & _pt, const SparsePoints & _points, double _scale)  {
	double radius = pow(_scale,l);
	if(_pt.length(_points[i]) > radius)  {
		std::cout << _pt << " not covered at level " << l << " by " << i << std::endl;
		return false;
	}
	else
		std::cout << "node covered at level " << l << " by " << i << std::endl;
	if(this->is_root())
		return true;
	return parent->fully_covers(_pt, _points, _scale);
}

bool CoverTreeNode::create_and_insert_node(int _i, int _l, int _pi)  {
	if(i == _pi)  {
		//std::cout << "creating and inserting node..." << std::endl;
		CoverTreeNode* parent_node = this->get_self_node(_l-1);
		if(parent_node->num_children() == 0)
			parent_node->insert_child(new CoverTreeNode(this,i,_l));
		parent_node->insert_child(new CoverTreeNode(this,_i,_l));
		return true;
	}

	for(int c = 0; c < children.size(); c++)  {
		CoverTreeNode* child_node = children[c];
		bool result = child_node->create_and_insert_node(_i,_l,_pi);
		if(result)
			return true;
	}

	return false;
}

CoverTreeNode* CoverTreeNode::get_self_node(int _l)  {
	if(_l == l)
		return this;
	for(int c = 0; c < children.size(); c++)  {
		CoverTreeNode* child_node = children[c];
		if(child_node->idx() == i)
			return child_node->get_self_node(_l);
	}
	CoverTreeNode* new_self = new CoverTreeNode(this,i,l-1);
	this->insert_child(new_self);
	return new_self->get_self_node(_l);
}
