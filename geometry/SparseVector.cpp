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



#include "SparseVector.h"

SparseVector::SparseVector()  {
	n = 0;
	q = 0;
}

SparseVector::SparseVector(string _filename)  {
}

SparseVector::SparseVector(int* _indices, double *_d, int _q, int _n)  {
	n = _n;
	q = _q;
	indices = new int[q];
	d = new double[q];

	for(int i = 0; i < q; i++)  {
		indices[i] = _indices[i];
		d[i] = _d[i];
	}
}

SparseVector::SparseVector(vector<int> _indices, vector<double> _d, int _n)  {
	n = _n;
	q = _indices.size();
	indices = new int[q];
	d = new double[q];

	for(int i = 0; i < q; i++)  {
		indices[i] = _indices[i];
		d[i] = _d[i];
	}
}

SparseVector::SparseVector(const SparseVector & _vector)  {
	n = _vector.dim();
	q = _vector.sparsity();
	indices = new int[q];
	d = new double[q];

	for(int i = 0; i < q; i++)  {
		SparseVectorEntry next_entry = _vector[i];
		indices[i] = next_entry.first;
		d[i] = next_entry.second;
	}
}

SparseVector::~SparseVector()  {
	delete [] d;
	delete [] indices;
}

double SparseVector::expected_l2Norm() const  {
	double exp_l2norm = 0;
	for(int i = 0; i < q; i++)
		exp_l2norm += d[i]*d[i];
	exp_l2norm *= ((double)n / (double)q);
	return exp_l2norm;
}

double SparseVector::expected_sqd_dist(const SparseVector & _vec, double _percCommon) const  {
	double sum = 0;
	int num_coincide = 0;
	unsigned our_counter = 0, other_counter = 0;
	while(our_counter < q && other_counter < _vec.sparsity())  {
		unsigned our_index = indices[our_counter];
		unsigned other_index = _vec.getIndex(other_counter);
		if(our_index == other_index)  {
			double p1_value = d[our_counter], p2_value = _vec.getEntry(other_counter);
			sum += (p1_value - p2_value)*(p1_value - p2_value);
			our_counter++;
			other_counter++;
			num_coincide++;
		}
		else if(our_index < other_index)
			our_counter++;
		else
			other_counter++;
	}

	//if(num_coincide == 0)
	//	cerr << "warning: bad distance!" << endl;

	int common_threshold = n*_percCommon;
	if(num_coincide < common_threshold)
		return -1;

	sum = 1.0*sum*((double)n/(double)num_coincide);
	return sum;
}

double SparseVector::expected_length(const SparseVector & _vec, double _percCommon) const  {
	double e_sqd_dist = this->expected_sqd_dist(_vec, _percCommon);
	return e_sqd_dist < 0 ? e_sqd_dist : sqrt(e_sqd_dist);
}

double SparseVector::expected_inner_product(const SparseVector & _vec, double _percCommon) const  {
	double sum = 0;
	int num_coincide = 0;
	unsigned our_counter = 0, other_counter = 0;
	while(our_counter < q && other_counter < _vec.sparsity())  {
		unsigned our_index = indices[our_counter];
		unsigned other_index = _vec.getIndex(other_counter);
		if(our_index == other_index)  {
			double p1_value = d[our_counter], p2_value = _vec.getEntry(other_counter);
			sum += (p1_value*p2_value);
			our_counter++;
			other_counter++;
			num_coincide++;
		}
		else if(our_index < other_index)
			our_counter++;
		else
			other_counter++;
	}

	//if(num_coincide == 0)
	//	cerr << "warning: bad distance!" << endl;

	int common_threshold = n*_percCommon;
	if(num_coincide < common_threshold)
		return 0;

	sum = 1.0*sum*((double)n/(double)num_coincide);
	return sum;
}

int SparseVector::sparsity_in_common(const SparseVector & _vec, bool _debug) const  {
	int num_coincide = 0;
	unsigned our_counter = 0, other_counter = 0;
	while(our_counter < q && other_counter < _vec.sparsity())  {
		unsigned our_index = indices[our_counter];
		unsigned other_index = _vec.getIndex(other_counter);
		if(our_index == other_index)  {
			double p1_value = d[our_counter], p2_value = _vec.getEntry(other_counter);
			if(_debug)
				cout << "["<<our_index<<"] : " << p1_value << " " << p2_value << endl;
			our_counter++;
			other_counter++;
			num_coincide++;
		}
		else if(our_index < other_index)
			our_counter++;
		else
			other_counter++;
	}
	return num_coincide;
}

bool SparseVector::has_dimension(int _dim, double & entry) const  {
	for(int i = 0; i < q; i++)  {
		if(indices[i] == _dim)  {
			entry = d[i];
			return true;
		}
	}
	return false;
}

SparsityPattern SparseVector::extract_missing_entries()  const  {
	bool* is_missing = new bool[n];
	for(unsigned i = 0; i < n; i++)
		is_missing[i] = true;
	for(unsigned i = 0; i < q; i++)
		is_missing[ indices[i] ] = false;

	SparsityPattern sparsity_pattern;
	for(unsigned i = 0; i < n; i++)  {
		if(is_missing[i])
			sparsity_pattern.push_back(i);
	}
	delete [] is_missing;
	return sparsity_pattern;
}

void SparseVector::write_to_file(string _filename)  {
}

double SparseVector::length(const SparseVector & _vec) const  {
	return sqrt(this->sqd_dist(_vec));
}

double SparseVector::sqd_dist(const SparseVector & _vec) const  {
	bool is_fully_dense = true;
	if(is_fully_dense)  {
		double squared_dist = 0, cur_diff = 0;
		for(int i = 0; i < n; i++)  {
			cur_diff = d[i]-_vec.getEntry(i);
			squared_dist += (cur_diff*cur_diff);
		}
		return squared_dist;
	}

	int our_iter = 0;
	int other_iter = 0;
	double sqdDist = 0;
	while(our_iter < this->sparsity() || other_iter < _vec.sparsity())  {
		if(other_iter == _vec.sparsity())  {
			sqdDist += d[our_iter]*d[our_iter];
			our_iter++;
			continue;
		}
		if(our_iter == q)  {
			sqdDist += _vec.getEntry(other_iter)*_vec.getEntry(other_iter);
			other_iter++;
			continue;
		}

		int our_ind = indices[our_iter], other_ind = _vec.getIndex(other_iter);
		double our_value = d[our_iter], other_value = _vec.getEntry(other_iter);
		if(our_ind == other_ind)  {
			double diff = our_value-other_value;
			sqdDist += diff*diff;
			our_iter++;
			other_iter++;
		}
		else if(our_ind < other_ind)  {
			sqdDist += our_value*our_value;
			our_iter++;
		}
		else  {
			sqdDist += other_value*other_value;
			other_iter++;
		}
	}
	return sqdDist;
}
