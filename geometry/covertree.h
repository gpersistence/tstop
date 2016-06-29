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



#ifndef COVERTREE_H
#define COVERTREE_H

#include "point_incs.h"
#include <set>

class CoverTreeNode  {
	public:
		CoverTreeNode(CoverTreeNode* _parent, int _i, int _l);
		CoverTreeNode(int _i, int _l);
		~CoverTreeNode();

		bool insert_child(CoverTreeNode* _node)  { children.push_back(_node); }
		int num_children()  { return children.size(); }
		CoverTreeNode* get_parent()  { return parent; }
		std::vector<CoverTreeNode*> get_children();

		int idx()  { return i; }
		int level()  { return l; }

		bool is_root()  { return !has_parent; }
		bool is_leaf()  { return children.size() == 0; }

		bool fully_covers(const SparseVector & _pt, const SparsePoints & _points, double _scale);

		void get_unique_nodes(std::vector<CoverTreeNode*>* nodes, std::set<int>* unique_ids);
		void get_all_child_nodes(std::vector<CoverTreeNode*>* nodes);

		void populate_parent_radii(std::vector<double>* node_radii, std::vector<double>* parent_radii, const SparsePoints & _points, double _scale);

		bool create_and_insert_node(int _i, int _l, int _pi);
		CoverTreeNode* get_self_node(int _l);

	private:
		int i, l;
		bool has_parent;
		CoverTreeNode* parent;
		std::vector<CoverTreeNode*> children;
};

class CoverTree  {
	public:
		CoverTree(const SparsePoints & _points, double _scale=2);
		CoverTree(const SparsePoints & _points, std::vector<int> _levels, std::vector<int> _parents, double _scale=2);
		~CoverTree();

		void build_tree();
		int insert_point(int _i);

		double distance_to_set(int _q, const std::vector<CoverTreeNode*> & _nodes);
		bool insert_point(int _q, const std::vector<CoverTreeNode*> & _coverSet, int _l, int & inserted_level);

		void check_invariants();

		double parent_radius(int _i)  { return parent_radii[_i]; }

		std::set<int> ball_query(SparseVector _pt, double _radius);

	private:
		SparsePoints points;
		double scale;

		SparseVector center;
		double diameter_ub;

		int root_level;

		bool is_constructed;
		CoverTreeNode* root_node;
		std::vector<double> parent_radii;

		std::vector<int> fps();

		bool debug;
};

#endif
