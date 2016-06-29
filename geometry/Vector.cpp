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



#include "Vector.h"

Vector::Vector()  {
	n = 0;
}

Vector::Vector(string _file)  {
	FILE* file_vector = fopen(_file.c_str(), "r");
	char line_raw[256];
	ifstream vec_file(_file.c_str());
	if (vec_file.fail())
		return;

	n = 0;
	vector<double> vec_array;
	for (;;)  {
		vec_file.getline(line_raw, 256);
		if (vec_file.eof())
			break;
		n++;
		string line(line_raw);
		vector<string> tokens;
		tokenize_line(&tokens, line, " \t");
		vec_array.push_back(atof(tokens[0].c_str()));
	}
	vec_file.close();

	d = new double[n];
	for(int i = 0; i < n; i++)
		d[i] = vec_array[i];
}

Vector::Vector(int _n)  {
	n = _n;
	d = new double[_n];
	for(int i = 0; i < n; i++)
		d[i] = 0.0;
}

Vector::Vector(double *_d, int _n)  {
	n = _n;
	d = new double[_n];
	for(int i = 0; i < n; i++)
		d[i] = _d[i];
}

Vector::Vector(vector<double> _vector)  {
	n = _vector.size();
	d = new double[n];
	for(int i = 0; i < n; i++)
		d[i] = _vector[i];
}

Vector::Vector(const Vector & _vector)  {
	n = _vector.dim();
	d = new double[n];
	for(int i = 0; i < n; i++)
		d[i] = _vector.getEntry(i);
}

Vector::Vector(Vector* _vector)  {
	n = _vector->dim();
	d = new double[n];
	for(int i = 0; i < n; i++)
		d[i] = _vector->getEntry(i);
}

Vector::Vector(boost::python::object object) {
  int obj_len = boost::python::len(object);
  bool initialized = false;
  if (obj_len == 1) {
    boost::python::extract<int> get_int(object);
    if (get_int.check()) {
      n = get_int();
      d = new double[n];
      for (int i = 0; i < n; i++) {
	d[i] = 0.0;
      }
      initialized = true;
    }
  }
  if (initialized == false) {
    boost::python::list obj_list = boost::python::extract<boost::python::list>(object);
    n = len(obj_list);
    d = new double[n];
    for (int i = 0; i < n; i++) {
      d[i] = boost::python::extract<double>(obj_list[i]);
      //      std::cout << d[i] << "," ;
    }
  }
}

Vector::~Vector()  {
	delete [] d;
}

double Vector::lInfNorm() const {
	double max_val = 0.0;
	for(int i = 0; i < n; i++)  {
		double abs_val = d[i] < 0 ? -d[i] : d[i];
		max_val = abs_val > max_val ? abs_val : max_val;
	}
	return max_val;
}

double Vector::l2Norm() const {
	double ssd = 0.0;
	for(int i = 0; i < n; i++)
		ssd += d[i]*d[i];
	return sqrt(ssd);
}

double Vector::l1Norm() const {
	double l1_norm = 0.0;
	for(int i = 0; i < n; i++)
		l1_norm += fabs(d[i]);
	return l1_norm;
}

double Vector::sqd_dist(const Vector & _vec) const {
	double squared_dist = 0, cur_diff = 0;
	for(int i = 0; i < n; i++)  {
		cur_diff = d[i]-_vec.getEntry(i);
		squared_dist += (cur_diff*cur_diff);
	}
	return squared_dist;
}

double Vector::length(const Vector & _vec) const  {
	return sqrt(this->sqd_dist(_vec));
}

double Vector::l_infinity_dist(const Vector & _vec) const {
	double max_dist = -1e10;
	for(int i = 0; i < n; i++)  {
		double cur_diff = d[i]-_vec.getEntry(i);
		if(cur_diff < 0) cur_diff = -cur_diff;
		max_dist = cur_diff > max_dist ? cur_diff : max_dist;
	}
	return max_dist;
}

double Vector::coherence() const  {
	double l2_norm = l2Norm(), linf_norm = lInfNorm();
	double coherence = (n * (linf_norm*linf_norm)) / (l2_norm*l2_norm);
	return coherence;
}

void Vector::normalize()  {
	double the_norm = l2Norm();
	if(the_norm < 1e-10)  {
		cout << "numerically zero norm!" << endl;
		return;
	}
	double inv_length = 1.0 / the_norm;
	for(int i = 0; i < n; i++)
		d[i] *= inv_length;
}

void Vector::minAndMax(int* min_index, double* minimum, int* max_index, double* maximum)  {
	double the_min = 1e10, the_max = -1e10;
	int min_ind = -1, max_ind = -1;
	for(int i = 0; i < n; i++)  {
		if(d[i] < the_min)  {
			the_min = d[i];
			min_ind = i;
		}
		if(d[i] > the_max)  {
			the_max = d[i];
			max_ind = i;
		}
	}

	*min_index = min_ind;
	*minimum = the_min;
	*max_index = max_ind;
	*maximum = the_max;
}

void Vector::min(int* index, double* minimum)  {
	double the_min = 1e10;
	int the_index = -1;
	for(int i = 0; i < n; i++)  {
		if(d[i] < the_min)  {
			the_min = d[i];
			the_index = i;
		}
	}
	*index = the_index;
	*minimum = the_min;
}

void Vector::max(int* index, double* maximum)  {
	double the_max = -1e10;
	int the_index = -1;
	for(int i = 0; i < n; i++)  {
		if(d[i] > the_max)  {
			the_max = d[i];
			the_index = i;
		}
	}
	*index = the_index;
	*maximum = the_max;
}

void Vector::expand_min_bound(const Vector & _vec)  {
	for(int i = 0; i < n; i++)  {
		d[i] = _vec.getEntry(i) < d[i] ? _vec.getEntry(i) : d[i];
	}
}

void Vector::expand_max_bound(const Vector & _vec)  {
	for(int i = 0; i < n; i++)  {
		d[i] = _vec.getEntry(i) > d[i] ? _vec.getEntry(i) : d[i];
	}
}

void Vector::tokenize_line(vector<string>* tokens, const string& input, string sep)  {
	string comm;
	for (unsigned int i = 0; i < input.size(); i++)  {
		const char ch = input[i];
		bool added = false;
		for (unsigned int s = 0; s < sep.size(); s++)  {
			if (ch == sep[s])  {
				tokens->push_back(comm);
				comm = "";
				added = true;
				break;
			}
		}
		if (!added)
			comm += ch;
	}
	if (comm != "")
		tokens->push_back(comm);
}

void Vector::write_to_file(string _filename, bool sort)  {
	FILE* vector_file = fopen(_filename.c_str(), "w");
	vector<double> func_vals;
	for(int i = 0; i < n; i++)
		func_vals.push_back(d[i]);
	if(sort)
		std::sort(func_vals.begin(),func_vals.end());
	for(int i = 0; i < n; i++)
		fprintf(vector_file, "%.7f\n", func_vals[i]);
	fclose(vector_file);
}

