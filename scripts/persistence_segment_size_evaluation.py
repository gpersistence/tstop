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


import csv
import multiprocessing
import os
import sys
import argparse
import importlib
import random
import itertools
import numpy
from persistence.Datatypes.JSONObject import save_data, load_data
from persistence.Datatypes.Configuration import Configuration
from persistence.Datatypes.Segments import Segment, Segments
from persistence.PersistenceGenerator import process, process_full
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagram, PersistenceDiagrams
from persistence.BottleneckDistances import BottleneckDistances
from persistence.WassersteinDistances import WassersteinDistances

def windows(data, data_type, segment_start, segment_size, window_size, window_stride, data_index) :
    if data_type == "CSVSegments" :
        windows = []
        for window_start in range(segment_start, 
                                  segment_start + segment_size - window_size + 1, 
                                  window_stride):
            window_end = window_start + window_size
            windows.append(list(itertools.chain(*itertools.izip(*[[float(d[i]) for d in data[window_start:window_end]] for i in data_index]))))
    elif data_type == "BirdSoundsSegments" :
        windows = [data[window_start:(window_start + window_size)] \
                   for window_start in range(segment_start, 
                                             segment_start + segment_size - window_size + 1, 
                                             window_stride)]
    else : 
        data_index = range(len(data[0][0]))
        windows = [[float(data[i][0][j]) for (i,j) in itertools.product(range(window_start, 
                                                                              window_start + window_size),
                                                                        data_index)]
                   for window_start in range(segment_start, 
                                             segment_start + segment_size - window_size + 1, 
                                             window_stride)]
    return windows

import time
def time_process(input) :
    start = time.time()
    if (input[1][0] < 0) :
        result = process_full(input)
    else :
        result = process(input)
    end = time.time()
    return (result, end - start)
    
def map_func((segment_data, bottleneck, wasserstein)) :
    start = time.time()
    bottleneck.compute_distances()
    stop = time.time()
    segment_data[0]['bottleneck_runtime'] = stop - start
    start = time.time()
    wasserstein.compute_distances()
    stop = time.time()
    segment_data[0]['wasserstein_runtime'] = stop - start
    print "Sample %s segment size %s runtime %s, %s" % (segment_data[0]['segment_start'], segment_data[0]['segment_size'], segment_data[0]['bottleneck_runtime'], segment_data[0]['wasserstein_runtime'])

    return (segment_data, [[d.toJSONDict() for d in row] for row in bottleneck.distances], [[d.toJSONDict() for d in row] for row in wasserstein.distances])


if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='Randomly generates segments from a given data file, data type, min/max segment size, segment size step size, window size, and then generates Persistence Diagrams for them with varying max simplices')
    parser.add_argument('--infile', nargs="+")
    parser.add_argument('--outfile', default='output')
    parser.add_argument('--type')
    parser.add_argument('--segments')
    parser.add_argument('--min-segment-size', default=400, type=int)
    parser.add_argument('--max-segment-size', default=1000, type=int)
    parser.add_argument('--segment-size-step', default=20, type=int)
    parser.add_argument('--window-size', default=40, type=int)
    parser.add_argument('--samples', default=10, type=int)
    parser.add_argument('--sample-at', default=None)
    parser.add_argument('--wasserstein', action='store_true')
    parser.add_argument('--pool', default=multiprocessing.cpu_count()-2, type=int)
    args = parser.parse_args(sys.argv[1:])
    if args.pool > 1 :
        pool = multiprocessing.Pool(args.pool)
    else :
        pool = itertools
        
    data = []
    if args.segments != None :
        segments_json = load_data(args.segments, 'segments', None, None, sys.argv[0] + ": ")
        segments = Segments.fromJSONDict(segments_json)
        args.type = segments.config.data_type
        config = segments.config
        config.window_size = args.window_size
        config.window_stride = 1
        for segment in segments.segments :
            point_len = len(segment.windows[0]) / segment.segment_size
            this_data = [(segment.windows[0][i:i+point_len], segment.filename)
                         for i in range(0, len(segment.windows[0]), point_len)]
            data.extend(this_data)
    else :
        config = Configuration.fromJSONDict(dict([('data_file', args.infile),
                                                  ('data_type', args.type),
                                                  ('window_size', args.window_size),
                                                  ('window_stride', 1),
                                                  ('threads', args.pool),
                                                  ('data_index', [1,2,3])]))
        for filename in args.infile :
            with open(filename, 'r') as data_file :
                if args.type == "BirdSoundsSegments" :
                    this_data = [float(line.strip()) for line in data_file]
                else :
                    data_reader = csv.reader(data_file, delimiter=',')
                    this_data = [([line[i] for i in config.data_index], filename) for line in data_reader]
                    this_data = this_data[0:len(this_data)]
                data.extend(this_data)
            # labels = set([d[1] for d in data])

    segments_module = importlib.import_module( 'persistence.' + args.type )
    segments_class = getattr(segments_module, args.type)


    tasks = []
    if args.sample_at != None :
        segment_start = [int(args.sample_at)]
    else :
        segment_start = random.sample(range(len(data) - args.max_segment_size), args.samples)

    for segment_size in range(args.min_segment_size, args.max_segment_size, args.segment_size_step) :
        config.segment_size = segment_size
        for start in segment_start :
            segment = Segment(windows       = windows(data, 
                                                      args.type, 
                                                      start, 
                                                      config.segment_size, 
                                                      config.window_size, 
                                                      config.window_stride,
                                                      config.data_index),
                              segment_start = start,
                              segment_size  = config.segment_size,
                              window_size   = config.window_size,
                              window_stride = config.window_stride,
                              labels        = None,
                              filename      = data[start][1] if args.type != "BirdSoundsSegments" else config.data_file,
                              data_index    = config.data_index,
                              label_index   = None)
            for alpha in [-1, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0] :
                config.max_simplices = int(segment_size * segment_size * alpha)
                tasks.append((segment,(config.max_simplices, None)))

    results = pool.imap(time_process, tasks)

    output = []
    i = 0
    for (task, (result, runtime)) in itertools.izip(tasks, results) :
        output.append(dict([('segment_start', task[0].segment_start), ('segment_size', task[0].segment_size), ('max_simplices', task[1][0]), ('runtime', runtime), ('diagram', result.toJSONDict())]))


    output.sort(key=lambda x: (x['segment_start'],x['max_simplices']/x['segment_size']/x['segment_size'], x['segment_size']))
    
    print "Distance Computation"

    samples = list(set([d['segment_start'] for d in output]))
    samples.sort()
    out_data = []
    for s in samples :
        sample_data = [d for d in output if d['segment_start'] == s]
        segment_sizes = list(set([x['segment_size'] for x in sample_data]))
        segment_sizes.sort()
        for size in segment_sizes :
            segment_data = [d for d in sample_data if d['segment_size'] == size]
            w_distances = WassersteinDistances(None,
                                               PersistenceDiagrams(None, [PersistenceDiagram.fromJSONDict(d['diagram']) for d in segment_data]),
                                               pool=None)
            distances = BottleneckDistances(None,
                                            PersistenceDiagrams(None, [PersistenceDiagram.fromJSONDict(d['diagram']) for d in segment_data]),
                                            pool=None)
            out_data.append((segment_data, distances, w_distances))
    goal = len(out_data)
    computed = pool.imap(map_func, out_data)
    done = []

    for (c,i) in itertools.izip(computed, range(goal)) :
        print "%d of %d" % (i, goal)
        done.append(c)
    save_data(args.outfile, done)
