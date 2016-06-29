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



#ifndef SPARSEVECTOR_H
#define SPARSEVECTOR_H

#include <algorithm>

#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdlib.h>
#include <math.h>

#include "Vector.h"

using namespace std;

typedef pair<int,double> SparseVectorEntry;
typedef std::vector<unsigned> SparsityPattern;

class SparseVector  {
	public:
		SparseVector();
		SparseVector(string _filename);
		SparseVector(int* _indices, double *_d, int _q, int _n);
		SparseVector(vector<int> _indices, vector<double> _d, int _n);
		SparseVector(const SparseVector & _vector);

		~SparseVector();

		int dim() const { return n; };
		int sparsity() const { return q; };

		SparseVector & operator=(const SparseVector & _vec)  {
			if(this == &_vec)
				return *this;
			if(n > 0)  {
				delete [] indices;
				delete [] d;
			}
			n = _vec.dim();
			q = _vec.sparsity();
			indices = new int[q];
			d = new double[q];

			for(int i = 0; i < q; i++)  {
				indices[i] = _vec.getIndex(i);
				d[i] = _vec.getEntry(i);
			}
			return *this;
		}

		SparseVectorEntry operator[](int _i) const  {
			return SparseVectorEntry(indices[_i],d[_i]);
		}

		Vector flatten_to_vector() const  {
			return Vector(d,q);
		}

		Vector subVector(const Vector & _vec) const  {
			Vector sub_vec(q);
			for(unsigned i = 0; i < q; i++)
				sub_vec.setEntry(i, _vec[ indices[i] ]);
			return sub_vec;
		}

		Vector zero_filled_vector() const  {
			Vector full_vec(n);
			for(int i = 0; i < q; i++)
				full_vec.setEntry(indices[i], d[i]);
			return full_vec;
		}

		double getEntry(int _i) const  {
			return d[_i];
		}
		int getIndex(int _i) const  {
			return indices[_i];
		}

		inline bool operator==(const SparseVector& _otherVec) const  {
			if(_otherVec.dim() != n || _otherVec.sparsity() != q)
				return false;
			for(int i = 0; i < q; i++)  {
				SparseVectorEntry next_entry = _otherVec[i];
				if(indices[i] != next_entry.first || d[i] != next_entry.second)
					return false;
			}
			return true;
		}

		double expected_l2Norm() const;
		double expected_sqd_dist(const SparseVector & _vec, double _percCommon=0) const;
		double expected_length(const SparseVector & _vec, double _percCommon=0) const;
		double expected_inner_product(const SparseVector & _vec, double _percCommon=0) const;
		int sparsity_in_common(const SparseVector & _vec, bool _debug=false) const;
		bool has_dimension(int _dim, double & entry) const;

		double length(const SparseVector & _vec) const;
		double sqd_dist(const SparseVector & _vec) const;

		SparsityPattern extract_missing_entries()  const;

		void write_to_file(string _filename);

		friend std::ostream& operator <<(std::ostream &out, const SparseVector & _vec)  {
			for(int i = 0; i < _vec.dim(); i++)  {
				SparseVectorEntry next_entry = _vec[i];
				out << " " << next_entry.first << " " << next_entry.second;
			}
			return out;
		}

	private:
		int* indices;
		double* d;
		int q;
		int n;
};

#endif
