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



#ifndef SEGMENT_DATASET_H
#define SEGMENT_DATASET_H

#include <string>
#include <vector>
#include <set>
#include <map>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdlib.h>

#include <Eigen/Dense>

struct LabeledSegment  {
	LabeledSegment(const Eigen::VectorXd & _segment, int _label) : segment(_segment) , label(_label)  {}
	Eigen::VectorXd segment;
	int label;
};

class SegmentDataset  {
	public:
		SegmentDataset(std::string _filename, double _trainingPerc=0.5);
		~SegmentDataset();

		int size()  { return labeled_segments.size(); }
		LabeledSegment get_segment(int _i)  { return labeled_segments[_i]; }

		void training_shuffle();

		int training_size()  {
			return training_inds.size();
		}

		std::vector<int> get_training_inds()  { return training_inds; }
		std::vector<int> get_test_inds()  { return test_inds; }

		LabeledSegment get_training_segment(int _i) const  {
			return labeled_segments[(training_inds[_i])];
		}

		int test_size()  {
			return test_inds.size();
		}

		LabeledSegment get_test_segment(int _i) const  {
			return labeled_segments[(test_inds[_i])];
		}

	private:
		double training_perc;
		std::vector<LabeledSegment> labeled_segments;
		std::set<int> all_labels;
		std::vector<int> training_inds;
		std::vector<int> test_inds;

		void tokenize_line(std::vector<std::string>* tokens, const std::string& input, std::string sep);
};

#endif
