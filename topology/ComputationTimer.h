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



#ifndef COMPUTATIONTIMER_H
#define COMPUTATIONTIMER_H

#include <time.h>
#include <iostream>
using namespace std;

class ComputationTimer  {
	public:
		ComputationTimer(string _computation);
		~ComputationTimer();

		void start()  { computation_start = clock(); }
		void end()  {
			computation_end = clock();
			total_time = ((double)(computation_end-computation_start)) / CLOCKS_PER_SEC;
		}

		string getComputation()  { return computation; }
		double getElapsedTime()  { return total_time; }
		void dump_time()  { cout << computation << " : " << total_time << " s " << endl; }

	private:
		clock_t computation_start, computation_end;
		double total_time;
		string computation;
};

#endif
