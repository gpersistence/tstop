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



#ifndef ZEROPERSISTENCE_H
#define ZEROPERSISTENCE_H

#include <vector>
#include <iostream>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <cstdlib>

struct FunctionValue  {
	FunctionValue() : ind(0) , t(0) , value(0) {}
	FunctionValue(int _ind, double _t, double _value) : ind(_ind) , t(_t) , value(_value) {}

	inline bool operator<(const FunctionValue& _ci) const {
		return value < _ci.value;
	}

	int ind;
	double t;
	double value;
};

class SublevelSet  {
	public:
		SublevelSet()  {
			minimum = 1e15;
			maximum = -1;
			is_empty = true;
			has_children = false;
			has_parent = false;
		}

		SublevelSet(FunctionValue _function)  {
			minimum = _function.value;
			tail_function = _function;
			head_function = _function;
			is_empty = false;
			has_children = false;
			has_parent = false;
		}

		SublevelSet(FunctionValue _function, SublevelSet* _tailChild, SublevelSet* _headChild)  {
			tail_child = _tailChild;
			head_child = _headChild;
			tail_child->assign_parent(this);
			head_child->assign_parent(this);
			double tail_minimum = tail_child->get_minimum();
			double head_minimum = head_child->get_minimum();
			minimum = tail_minimum < head_minimum ? tail_minimum : head_minimum;
			maximum = _function.value;
			tail_function = tail_child->get_tail_function();
			head_function = head_child->get_head_function();
			is_empty = false;
			has_children = true;
			has_parent = false;
		}

		~SublevelSet()  {
			if(has_children)  {
				delete tail_child;
				delete head_child;
			}
		}

		void assign_parent(SublevelSet* _parent)  {
			parent_node = _parent;
			has_parent = true;
		}

		double get_minimum()  {
			if(has_children)  {
				double tail_minimum = tail_child->get_minimum();
				double head_minimum = head_child->get_minimum();
				return tail_minimum < head_minimum ? tail_minimum : head_minimum;
			}
			else
				return minimum;
		}

		double persistence()  {
			return maximum == -1 ? -1 : maximum-minimum;
		}

		SublevelSet* get_root()  {
			if(has_parent)
				return parent_node->get_root();
			else
				return this;
		}

		FunctionValue get_tail_function()  {
			return tail_function;
		}

		FunctionValue get_head_function()  {
			return head_function;
		}

		bool is_sublevelset_empty()  { return is_empty; }

		bool expand_set(FunctionValue _func)  {
			if(_func.ind == tail_function.ind-1)  {
				tail_function = _func;
				return true;
			}
			else if(_func.ind == head_function.ind+1)  {
				head_function = _func;
				return true;
			}
			else  {
				std::cerr << "point can not expand sublevel set!" << std::endl;
				return false;
			}
		}

		std::pair<double,double> persistence_pairing()  {
			// no children -> no pairing
			if(!has_children)
				return std::pair<double,double>(-1,-1);
			// the child whose minimum is largest represents the component which was merged
			double tail_minimum = tail_child->get_minimum();
			double head_minimum = head_child->get_minimum();
			if(tail_minimum > head_minimum)
				return std::pair<double,double>(tail_minimum,maximum);
			else
				return std::pair<double,double>(head_minimum,maximum);
		}

		void compute_all_pairs(std::vector<std::pair<double,double> > & pd)  {
			// no children -> no pairing
			if(!has_children)
				return;
			pd.push_back(this->persistence_pairing());
			tail_child->compute_all_pairs(pd);
			head_child->compute_all_pairs(pd);
		}

		void get_prominent_sublevelsets(double _thresh, std::vector<SublevelSet*> & prominent_sublevelsets)  {
			if(!has_children)  {
				//prominent_sublevelsets.push_back(this);
				return;
			}

			std::pair<double,double> pairing = this->persistence_pairing();
			double persistence = pairing.second-pairing.first;
			if(persistence > _thresh)
				prominent_sublevelsets.push_back(this);
			tail_child->get_prominent_sublevelsets(_thresh, prominent_sublevelsets);
			head_child->get_prominent_sublevelsets(_thresh, prominent_sublevelsets);
		}

	private:
		bool is_empty;
		bool has_children;
		bool has_parent;
		double minimum;
		double maximum;
		FunctionValue tail_function, head_function;

		SublevelSet* parent_node;
		SublevelSet* tail_child;
		SublevelSet* head_child;
};

class GrowingComponent  {
	public:
		GrowingComponent(int _ind, double _minima)  {
			left_ind = _ind;
			right_ind = _ind;
			minima = _minima;
		}
		~GrowingComponent();

		int left_ind, right_ind;
		double minima;
};

class ZeroPersistence  {
	private:
		std::vector<FunctionValue> function;
		std::vector<SublevelSet*> all_sublevelsets;
		SublevelSet** sublevelset_assignments;
		SublevelSet* root_sublevelset;

		bool is_less(int _i, double _fi, int _j, double _fj)  {
			if(_fi == _fj)
				return _i < _j;
			return _fi < _fj;
		}

		bool is_greater(int _i, double _fi, int _j, double _fj)  {
			if(_fi == _fj)
				return _i > _j;
			return _fi > _fj;
		}
	public:
		ZeroPersistence(const std::vector<FunctionValue> & _function);
		~ZeroPersistence();

		void sweep_persistence();
		void growing_persistence();

		void write_pd_to_file(std::string _filename);
		SublevelSet *get_root() {return this->root_sublevelset; }

};

#endif
