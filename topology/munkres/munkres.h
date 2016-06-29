/*
 *   Copyright (c) 2007 John Weaver
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 */

#if !defined(_MUNKRES_H_)
#define _MUNKRES_H_

#include <Eigen/Dense>

#include <list>
#include <utility>
#include <queue>
#include "../ComputationTimer.h"

class PairCompare  {
	public:
		bool operator()(std::pair<int,int> _p1, std::pair<int,int> _p2)  {
			if(_p1.first < _p2.first)
				return false;
			else if(_p1.first > _p2.first)
				return true;
			else  {
				return _p1.second > _p2.second;
			}
		}
};

class Munkres {
public:
	void solve(Eigen::MatrixXd &m);
private:
  static const int NORMAL = 0;
  static const int STAR = 1;
  static const int PRIME = 2; 
	inline bool find_uncovered_in_matrix(double,int&,int&);
	inline bool pair_in_list(const std::pair<int,int> &, const std::list<std::pair<int,int> > &);
	int step1(void);
	int step2(void);
	int step3(void);
	int step4(void);
	int step5(void);
	int step6(void);
	Eigen::MatrixXi mask_matrix;
	Eigen::MatrixXd matrix;
	bool *row_mask;
	bool *col_mask;
	int saverow, savecol;

	//bool 
};

#endif /* !defined(_MUNKRES_H_) */
