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



#include "zero_persistence.h"

ZeroPersistence::ZeroPersistence(const std::vector<FunctionValue> & _function)  {
	function = _function;
}

ZeroPersistence::~ZeroPersistence()  {
}

void ZeroPersistence::sweep_persistence()  {
	std::vector<FunctionValue> sorted_function = function;
	std::sort(sorted_function.begin(),sorted_function.end());

	int n = sorted_function.size();
	// initialize sublevel set assignments to be all empty
	SublevelSet* empty_sublevelset = new SublevelSet();
	sublevelset_assignments = new SublevelSet*[n];
	for(int i = 0; i < n; i++)
		sublevelset_assignments[i] = empty_sublevelset;

	SublevelSet* active_sublevelset = empty_sublevelset;
	int num_minima = 0, num_maxima = 0;
	for(int i = 0; i < n; i++)  {
		FunctionValue function_val = sorted_function[i];
		int ind = function_val.ind;
		double t = function_val.t;
		double f = function_val.value;

		// find sublevel set whose tail/head contains ind+1/ind-1 -> if both, then merging them
		if((ind > 0 && !sublevelset_assignments[ind-1]->is_sublevelset_empty()) && (ind < (n-1) && !sublevelset_assignments[ind+1]->is_sublevelset_empty()))  {
			SublevelSet* left_sublevelset = sublevelset_assignments[ind-1]->get_root();
			SublevelSet* right_sublevelset = sublevelset_assignments[ind+1]->get_root();
			SublevelSet* merged_sublevelset = new SublevelSet(function_val,left_sublevelset,right_sublevelset);
			sublevelset_assignments[ind] = merged_sublevelset;
			num_maxima++;
		}
		else if(ind > 0 && !sublevelset_assignments[ind-1]->is_sublevelset_empty())  {
			SublevelSet* left_sublevelset = sublevelset_assignments[ind-1]->get_root();
			left_sublevelset->expand_set(function_val);
			sublevelset_assignments[ind] = left_sublevelset;
		}
		else if(ind < (n-1) && !sublevelset_assignments[ind+1]->is_sublevelset_empty())  {
			SublevelSet* right_sublevelset = sublevelset_assignments[ind+1]->get_root();
			right_sublevelset->expand_set(function_val);
			sublevelset_assignments[ind] = right_sublevelset;
		}
		else  { // new component!
			SublevelSet* new_sublevelset = new SublevelSet(function_val);
			sublevelset_assignments[ind] = new_sublevelset;
			num_minima++;
		}
		active_sublevelset = sublevelset_assignments[ind];
	}
	root_sublevelset = active_sublevelset;

	std::vector<std::pair<double,double> > zero_pd;
	active_sublevelset->compute_all_pairs(zero_pd);

	std::vector<double> all_persistence_values;
	for(int i = 0; i < zero_pd.size(); i++)
		all_persistence_values.push_back(zero_pd[i].second-zero_pd[i].first);
	std::sort(all_persistence_values.begin(),all_persistence_values.end());
	//for(int i = 0; i < all_persistence_values.size(); i++)
	//	std::cout << "persistence["<<i<<"] : " << all_persistence_values[i] << std::endl;
	//std::cout << "number of minima: " << num_minima << " ; number of maxima: " << num_maxima << " ; number of persistence pairings: " << zero_pd.size() << std::endl;
}

void ZeroPersistence::growing_persistence()  {
	// first pass: find all minima and maxima
	/*
	std::vector<int> minima_inds, maxima_inds;
	std::vector<bool> vertex_minima(function.size(),false);
	std::vector<bool> vertex_maxima(function.size(),false);
	for(int i = 0; i < function.size(); i++)  {
		if(i == 0)  {
			if(is_less(i,f, i+1,function[i+1].value))
				minima_inds.push_back(i);
			else
				maxima_inds.push_back(i);
			continue;
		}
		else if(i == (function.size()-1))  {
			if(is_less(i,f, i-1,function[i-1].value))
				minima_inds.push_back(i);
			else
				maxima_inds.push_back(i);
			continue;
		}

		double f = function[i].value, p_f = function[i-1].value, n_f = function[i+1].value;
		if(is_less(i,f, i-1,p_f) && is_less(i,f, i+1,n_f))
			minima_inds.push_back(i);
		else if(is_greater(i,f, i-1,p_f) && is_greater(i,f, i+1,n_f))
			maxima_inds.push_back(i);
	}
	for(int i = 0; i < minima_inds.size(); i++)
		vertex_minima[(minima_inds[i])] = true;
	for(int i = 0; i < maxima_inds.size(); i++)
		vertex_maxima[(maxima_inds[i])] = true;

	// second pass: grow out components
	std::vector<GrowingComponent*> grown_components;
	// initialize all growing components with minima - grow each one until we hit maxima
	for(int i = 0; i < minima_inds.size(); i++)  {
		int min_ind = minima_inds[i];
		double minima_func = function[min_ind].value;
		GrowingComponent* growing_component = new GrowingComponent(min_ind, minima_func);
		bool hit_maxima = false;
		while(!hit_maxima)  {
			// grow component by smaller value of left and right indices
			int left_ind = growing_component->left_ind-1, right_ind = growing_component->right_ind+1;
			// take care of boundary conditions
			if(left_ind < 0)  {
			}
			else if(right_ind == function.size())  {
			}
			// standard growing
			else  {
			}
		}
	}
	*/
}

void ZeroPersistence::write_pd_to_file(std::string _filename)  {
	std::vector<std::pair<double,double> > zero_pd;
	root_sublevelset->compute_all_pairs(zero_pd);
	FILE* file = fopen(_filename.c_str(), "w");
	for(int i = 0; i < zero_pd.size(); i++)
		fprintf(file, "%.7f %.7f\n", zero_pd[i].first,zero_pd[i].second);
	fclose(file);
}
