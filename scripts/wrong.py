#TSTOP
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Learning import Learning, LearningResult
from persistence.Datatypes.TrainTestPartitions import TrainTestPartitions

partitions_json = load_data(sys.argv[1], 'partition', None, None, sys.argv[0] + ": ")
partitions = TrainTestPartitions.fromJSONDict(partitions_json)
all_wrongs = []
for f in sys.argv[2:] :
    results_json = load_data(f, 'learning', None, None, sys.argv[0] + ": ")
    results = Learning.fromJSONDict(results_json)
    wrongs = []
    for (result, partition) in zip(results.results, partitions.evaluation) :
        correct = [(l == r) for (l,r) in zip(result.test_labels, result.test_results)]
        wrong = [p for (c,p) in zip(correct, partition.test) if not c]
        wrong.sort()
        wrongs.append(wrong)
    all_wrongs.append(wrongs)

for (a,b) in zip(all_wrongs[0], all_wrongs[1]) :
    if a == b :
        print "identical"
    else :
        print "not identical"
