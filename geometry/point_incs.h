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



#ifndef POINTINC_H
#define POINTINC_H

#include "SparseVector.h"
#include "Vector.h"
#include "../ext/ANN/ANN/ANN.h"

typedef vector<Vector> Points;
typedef vector<SparseVector> SparsePoints;

struct IndexedDouble  {
	IndexedDouble() : ind(0) , value(0) {}
	IndexedDouble(int _ind, double _value) : ind(_ind) , value(_value) {}

	inline bool operator<(const IndexedDouble& _ci) const {
		return value < _ci.value;
	}

	int ind;
	double value;
};

class PointsIO  {

	public:
		static void write_points_to_file(string _filename, const Points & _points)  {
			FILE* points_file=fopen(_filename.c_str(),"w");
			for(unsigned i = 0; i < _points.size(); i++)  {
				Vector pt_i = _points[i];
				for(unsigned j = 0; j < pt_i.dim(); j++)  {
					if(j != pt_i.dim()-1)
						fprintf(points_file, "%.7f ", pt_i.getEntry(j));
					else
						fprintf(points_file, "%.7f\n", pt_i.getEntry(j));
				}
			}
			fclose(points_file);
		}

		static bool read_points_from_file(string _filename, Points & points)  {
			ifstream input_file(_filename.c_str());
			string line;
			while(std::getline(input_file,line))  {
				std::stringstream linestream(line);
				vector<double> all_entries;
				double x;
				while (linestream >> x)
					all_entries.push_back(x);
				points.push_back(Vector(all_entries));
			}
			input_file.close();
			return true;
		}

		static bool read_labeled_points_from_file(string _filename, Points & points, int & label)  {
			ifstream input_file(_filename.c_str());
			string line;
			int line_num = 1;
			while(std::getline(input_file,line))  {
				std::stringstream linestream(line);
				if(line_num == 1)  {
					linestream >> label;
					line_num++;
					continue;
				}

				vector<double> all_entries;
				double x;
				while (linestream >> x)
					all_entries.push_back(x);
				points.push_back(Vector(all_entries));
				line_num++;
			}
			input_file.close();
			return true;
		}

		static void write_sparse_points_to_file(string _filename, const SparsePoints & _points)  {
			FILE* points_file=fopen(_filename.c_str(),"w");
			fprintf(points_file, "%u\n", _points[0].dim());
			for(unsigned i = 0; i < _points.size(); i++)  {
				SparseVector pt_i = _points[i];
				for(unsigned j = 0; j < pt_i.sparsity(); j++)  {
					if(j != pt_i.sparsity()-1)
						fprintf(points_file, "%u %.7f ", pt_i.getIndex(j), pt_i.getEntry(j));
					else
						fprintf(points_file, "%u %.7f\n", pt_i.getIndex(j), pt_i.getEntry(j));
				}
			}
			fclose(points_file);
		}

		static void write_sparse_points_to_grouse_file(string _rowFilename, string _columnFilename, string _entryFilename, const SparsePoints & _points)  {
			FILE* row_file=fopen(_rowFilename.c_str(),"w");
			FILE* column_file=fopen(_columnFilename.c_str(),"w");
			FILE* entry_file=fopen(_entryFilename.c_str(),"w");
			for(unsigned i = 0; i < _points.size(); i++)  {
				SparseVector pt_i = _points[i];
				for(unsigned j = 0; j < pt_i.sparsity(); j++)  {
					fprintf(row_file, "%u\n", (pt_i.getIndex(j)+1));
					fprintf(column_file, "%u\n", (i+1));
					fprintf(entry_file, "%.7f\n", pt_i.getEntry(j));
				}
			}
			fclose(row_file);
			fclose(column_file);
			fclose(entry_file);
		}

		static bool read_sparse_points_from_file(string _filename, SparsePoints & points)  {
			ifstream input_file(_filename.c_str());
			string line;
			int line_num = 0, n = 0;
			while(std::getline(input_file,line))  {
				if(line_num == 0)  {
					stringstream linestream(line);
					linestream >> n;
					line_num++;
					continue;
				}
				line_num++;

				std::stringstream linestream(line);
				vector<double> all_entries;
				vector<int> all_indices;
				double x;
				int ind;
				while (linestream >> ind)  {
					linestream >> x;
					all_entries.push_back(x);
					all_indices.push_back(ind);
				}
				SparseVector sparse_vector(all_indices,all_entries,n);
				points.push_back(sparse_vector);
			}
			input_file.close();
			return true;
		}

		static void write_perseus_distance_matrix(string _filename, const Points & _points, int _dimCap)  {
			int num_points = _points.size();
			double** distance_matrix = new double*[num_points];

			for(int i = 0; i < num_points; i++)  {
				distance_matrix[i] = new double[num_points];
				distance_matrix[i][i]=0;
			}
			for(int i = 0; i < num_points; i++)  {
				for(int j = 0; j < i; j++)  {
					distance_matrix[i][j] = _points[i].length(_points[j]);
					distance_matrix[j][i] = distance_matrix[i][j];
				}
			}

			// figure out minimum distance, compute diameter
			double min_dist = 1e10, max_min_dist = -1, diameter = -1;
			for(int i = 0; i < num_points; i++)  {
				vector<double> i_dists;
				for(int j = 0; j < num_points; j++)
					i_dists.push_back(distance_matrix[i][j]);
				sort(i_dists.begin(),i_dists.end());
				double local_min_dist = i_dists[1], local_max_dist = i_dists[num_points-1];

				min_dist = local_min_dist < min_dist ? local_min_dist : min_dist;
				max_min_dist = local_min_dist > max_min_dist ? local_min_dist : max_min_dist;
				diameter = local_max_dist > diameter ? local_max_dist : diameter;
			}
			//min_dist *= 0.5;
			cout << "min dist: " << min_dist << " max min dist: " << max_min_dist << endl;

			// number of filtration intervals is diameter/min_dist
			int num_filtration_intervals = diameter/min_dist;

			FILE* perseus_file = fopen(_filename.c_str(),"w");
			fprintf(perseus_file, "%u\n", num_points);
			fprintf(perseus_file, "0 %.7f %u %u\n", min_dist, num_filtration_intervals, _dimCap);
			for(int i = 0; i < num_points; i++)  {
				for(int j = 0; j < num_points; j++)  {
					if(j == (num_points-1))
						fprintf(perseus_file, "%.7f\n", distance_matrix[i][j]);
					else
						fprintf(perseus_file, "%.7f ", distance_matrix[i][j]);
				}
			}
			fclose(perseus_file);

			for(int i = 0; i < num_points; i++)
				delete [] distance_matrix[i];
			delete [] distance_matrix;
		}

		static void write_perseus_distance_matrix(string _filename, const SparsePoints & _points, int _dimCap)  {
			int num_points = _points.size();
			double** distance_matrix = new double*[num_points];

			for(int i = 0; i < num_points; i++)  {
				distance_matrix[i] = new double[num_points];
				distance_matrix[i][i]=0;
			}
			for(int i = 0; i < num_points; i++)  {
				for(int j = 0; j < i; j++)  {
					distance_matrix[i][j] = _points[i].expected_length(_points[j]);
					distance_matrix[j][i] = distance_matrix[i][j];
				}
			}

			// figure out minimum distance, compute diameter
			double min_dist = 1e10, max_min_dist = -1, diameter = -1;
			for(int i = 0; i < num_points; i++)  {
				vector<double> i_dists;
				for(int j = 0; j < num_points; j++)
					i_dists.push_back(distance_matrix[i][j]);
				sort(i_dists.begin(),i_dists.end());
				double local_min_dist = i_dists[1], local_max_dist = i_dists[num_points-1];

				min_dist = local_min_dist < min_dist ? local_min_dist : min_dist;
				max_min_dist = local_min_dist > max_min_dist ? local_min_dist : max_min_dist;
				diameter = local_max_dist > diameter ? local_max_dist : diameter;
			}
			//min_dist *= 0.5;
			cout << "min dist: " << min_dist << " max min dist: " << max_min_dist << endl;

			// number of filtration intervals is diameter/min_dist
			int num_filtration_intervals = diameter/min_dist;

			FILE* perseus_file = fopen(_filename.c_str(),"w");
			fprintf(perseus_file, "%u\n", num_points);
			fprintf(perseus_file, "0 %.7f %u %u\n", min_dist, num_filtration_intervals, _dimCap);
			for(int i = 0; i < num_points; i++)  {
				for(int j = 0; j < num_points; j++)  {
					if(j == (num_points-1))
						fprintf(perseus_file, "%.7f\n", distance_matrix[i][j]);
					else
						fprintf(perseus_file, "%.7f ", distance_matrix[i][j]);
				}
			}
			fclose(perseus_file);

			for(int i = 0; i < num_points; i++)
				delete [] distance_matrix[i];
			delete [] distance_matrix;
		}

		static void nearest_neighbors(const SparsePoints & _points, double & min_dist, double & ave_dist, double & max_min_dist)  {
			int num_points = _points.size();
			double** distance_matrix = new double*[num_points];

			for(int i = 0; i < num_points; i++)  {
				distance_matrix[i] = new double[num_points];
				distance_matrix[i][i]=0;
			}
			for(int i = 0; i < num_points; i++)  {
				for(int j = 0; j < i; j++)  {
					distance_matrix[i][j] = _points[i].expected_length(_points[j]);
					distance_matrix[j][i] = distance_matrix[i][j];
				}
			}

			// figure out minimum distance, compute diameter
			min_dist = 1e10;
			max_min_dist = -1;
			ave_dist = 0;
			for(int i = 0; i < num_points; i++)  {
				vector<double> i_dists;
				for(int j = 0; j < num_points; j++)
					i_dists.push_back(distance_matrix[i][j]);
				sort(i_dists.begin(),i_dists.end());
				double local_min_dist = i_dists[1];

				min_dist = std::min(min_dist,local_min_dist);
				max_min_dist = std::max(max_min_dist,local_min_dist);
				ave_dist += local_min_dist;
			}
			ave_dist /= num_points;

			for(int i = 0; i < num_points; i++)
				delete [] distance_matrix[i];
			delete [] distance_matrix;
		}

		static void nearest_neighbors(const Points & _points, double & min_dist, double & ave_dist, double & max_min_dist)  {
			int num_points = _points.size();
			double** distance_matrix = new double*[num_points];

			for(int i = 0; i < num_points; i++)  {
				distance_matrix[i] = new double[num_points];
				distance_matrix[i][i]=0;
			}
			for(int i = 0; i < num_points; i++)  {
				for(int j = 0; j < i; j++)  {
					distance_matrix[i][j] = _points[i].length(_points[j]);
					distance_matrix[j][i] = distance_matrix[i][j];
				}
			}

			// figure out minimum distance, compute diameter
			min_dist = 1e10;
			max_min_dist = -1;
			ave_dist = 0;
			for(int i = 0; i < num_points; i++)  {
				vector<double> i_dists;
				for(int j = 0; j < num_points; j++)
					i_dists.push_back(distance_matrix[i][j]);
				sort(i_dists.begin(),i_dists.end());
				double local_min_dist = i_dists[1];

				min_dist = std::min(min_dist,local_min_dist);
				max_min_dist = std::max(max_min_dist,local_min_dist);
				ave_dist += local_min_dist;
			}
			ave_dist /= num_points;

			for(int i = 0; i < num_points; i++)
				delete [] distance_matrix[i];
			delete [] distance_matrix;
		}
};

class PointFinder  {
	public:
		PointFinder(const Points & _points) : points(_points), has_kdtree(false)  {}
		~PointFinder()  {}

		int gather_neighbors(Vector _query, int _numPts, int* neighbor_inds)  {
			int d = points[0].dim();
			if(!has_kdtree)  {
				point_array = annAllocPts(points.size(), d);
				for(unsigned v = 0; v < points.size(); v++)  {
					Vector point = points[v];
					for(int i = 0; i < d; i++)
						point_array[v][i] = point[i];
				}
				kd_tree = new ANNkd_tree(point_array, points.size(), d);
				has_kdtree = true;
			}

			int num_pts = _numPts;
			if(_numPts > points.size())  {
				cerr << "kdtree query error: more neighbors than points! using number of points instead ..." << endl;
				num_pts = points.size();
			}

			ANNidxArray nnIdx = new ANNidx[num_pts];
			ANNdistArray dists = new ANNdist[num_pts];

			ANNpoint query_pt = annAllocPt(d);
			for(int i = 0; i < d; i++)
				query_pt[i] = _query[i];

			kd_tree->annkSearch(query_pt, num_pts, nnIdx, dists);
			for(int i = 0; i < num_pts; i++)
				neighbor_inds[i] = nnIdx[i];

			delete [] nnIdx;
			delete [] dists;
			annDeallocPt(query_pt);

			return num_pts;
		}

		vector<int> gather_eps_ball(Vector _query, double _epsSqd)  {
			int d = points[0].dim();
			if(!has_kdtree)  {
				point_array = annAllocPts(points.size(), d);
				for(unsigned v = 0; v < points.size(); v++)  {
					Vector point = points[v];
					for(int i = 0; i < d; i++)
						point_array[v][i] = point[i];
				}
				kd_tree = new ANNkd_tree(point_array, points.size(), d);
				has_kdtree = true;
			}
			vector<int> nns;

			ANNpoint query_pt = annAllocPt(d);
			for(int i = 0; i < d; i++)
				query_pt[i] = _query[i];

			int k = kd_tree->annkFRSearch(query_pt, _epsSqd, 0, NULL, NULL, 0);
			annDeallocPt(query_pt);

			if(k == 0)
				return nns;

			int* neighbor_inds = new int[k];
			gather_neighbors(_query, k, neighbor_inds);
			for(int i = 0; i < k; i++)
				nns.push_back(neighbor_inds[i]);
			delete [] neighbor_inds;

			return nns;
		}

	private:
		Points points;
		bool has_kdtree;

		ANNpointArray point_array;
		ANNkd_tree* kd_tree;
};

#endif
