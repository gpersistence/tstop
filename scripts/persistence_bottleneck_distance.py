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


import argparse
import os
import sys
import subprocess
import multiprocessing
import time
import itertools
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagram, PersistenceDiagrams
from persistence.BottleneckDistances import BottleneckDistances
from persistence.WassersteinDistances import WassersteinDistances

def map_func((segment_data, bottleneck)) :
    start = time.time()
    bottleneck.compute_distances()
    stop = time.time()
    segment_data[0]['distance_runtime'] = stop - start
    print "Sample %s segment size %s runtime %s" % (segment_data[0]['segment_start'], segment_data[0]['segment_size'], segment_data[0]['distance_runtime'])

    return (segment_data, [[d.toJSONDict() for d in row] for row in bottleneck.distances])

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='Randomly generates segments from a given data file, data type, min/max segment size, segment size step size, window size, and then generates Persistence Diagrams for them with varying max simplices')
    parser.add_argument('--infile', nargs="+")
    parser.add_argument('--wasserstein', action='store_true')
    parser.add_argument('--outfile')
    parser.add_argument('--pool', default=multiprocessing.cpu_count(), type=int)
    args = parser.parse_args(sys.argv[1:])
    infiles = []
    for f in args.infile :
        (dirname,basename) = os.path.split(f)
        cmd = ["find", dirname, "-name", basename + "*", "-type", "f"]
        print " ".join(cmd)
        files = subprocess.check_output(cmd)
        files = files.split()
        infiles.extend(files)
    infiles.sort()
    print "\n".join(infiles)
    input_data = []
    for f in infiles :
        input_json = load_data(f, '', None, None, "persistence_bottleneck_distance.py : ")
        input_data.extend(input_json)

    input_data = [i for i in input_data if i['segment_start'] != i['segment_size']]
    input_data.sort(key=lambda x: (x['segment_start'],x['max_simplices']/x['segment_size']/x['segment_size'], x['segment_size']))
    #    for entry in input_data :
    #        print entry['segment_start'], entry['segment_size'], entry['max_simplices']

    samples = list(set([d['segment_start'] for d in input_data]))
    samples.sort()
    if args.pool > 1 :
        pool = multiprocessing.Pool(args.pool)
    else :
        pool = itertools
    out_data = []
    for s in samples :
        sample_data = [d for d in input_data if d['segment_start'] == s]
        segment_sizes = list(set([x['segment_size'] for x in sample_data]))
        segment_sizes.sort()
        for size in segment_sizes :
            segment_data = [d for d in sample_data if d['segment_size'] == size]
            if args.wasserstein : 
                distances = WassersteinDistances(None,
                                                 PersistenceDiagrams(None, [PersistenceDiagram.fromJSONDict(d['diagram']) for d in segment_data]),
                                                 pool=None)
            else :
                distances = BottleneckDistances(None,
                                                PersistenceDiagrams(None, [PersistenceDiagram.fromJSONDict(d['diagram']) for d in segment_data]),
                                                pool=None)
            out_data.append((segment_data, distances))
    goal = len(out_data)
    computed = pool.imap(map_func, out_data)
    done = []
    for (c,i) in itertools.izip(computed, range(goal)) :
        print "%d of %d" % (i, goal)
        done.append(c)
    save_data(args.outfile, done)
