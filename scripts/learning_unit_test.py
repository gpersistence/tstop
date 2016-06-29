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


#!/usr/bin/python

import os
import sys
import subprocess
import argparse
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("stage", default=0, type=int)
parser.add_argument("--pool", type=int)
args = parser.parse_args(sys.argv[1:])

if args.pool == None : 
    pool = str(multiprocessing.cpu_count())
else :
    pool = str(args.pool)

current_directory = os.getcwd()
out_dir = current_directory + "/unit_test_output"
stage = 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Segment generation with CSVSegments" % (stage,)
    segment_command = "python -O -m persistence.Datatypes.Segments --max-simplices 50000 " + \
                      "--segment-stride 3000 --segment-size 3000 --window-size 20 " + \
                      "--window-stride 1 --data-index 3 --label-index 4 " + \
                      "--data-file /home/daviss/data/activity/1.csv --data-type CSVSegments " + \
                      "--threads 1 --learning-split 0.2 --learning-iterations 50 " + \
                      "--kernel-scale 0.5 --persistence-degree 1"
    # adding directories at the end in case they contain whitespace...
    subprocess.call(segment_command.split() + 
                    ["--out-directory", out_dir, 
                     "--outfile", "%s/%s" % (out_dir, "CSVSegment.json")])

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Persistence generation with CSVSegments" % (stage,)
    persistence = subprocess.Popen(["python", "-O", "-m", "persistence.PersistenceGenerator", 
                                    "--infile", "%s/%s" % (out_dir, "CSVSegment.json"),
                                    "--outfile", "%s/%s" % (out_dir, "CSVPersistence.json"),
                                    "--pool", pool], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = persistence.communicate()

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Kernel generation with CSVSegments" % (stage,)
    subprocess.call(["python", "-O", "-m", "persistence.PersistenceKernel", 
                     "--infile", "%s/%s" % (out_dir, "CSVPersistence.json"),
                     "--outfile", "%s/%s" % (out_dir, "CSVKernel.json"),
                     "--pool", pool])

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Learning with CSVSegments" % (stage,)
    subprocess.call(["python", "-O", "-m", "persistence.KernelLearning", 
                     "--infile", "%s/%s" % (out_dir, "CSVKernel.json"),
                     "--outfile", "%s/%s" % (out_dir, "CSVLearning.json"),
                     "--pool", pool])

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Segment generation with UCRSegments" % (stage,)
    segment_command = "python -O -m persistence.Segments --max-simplices 50000 " + \
                      "--window-size 20 --window-stride 1 --data-type UCRSegments " + \
                      "--threads 1 --kernel-scale 0.5 --persistence-degree 1"
    # adding directories at the end in case they contain whitespace...
    subprocess.call(segment_command.split() + 
                    ["--data-file",  
                     "/home/daviss/data/time series data/50words/50words_TRAIN:/home/daviss/data/time series data/50words/50words_TEST",
                     "--out-directory", out_dir, 
                     "--outfile", "%s/%s" % (out_dir, "TimeSeriesSegment.json")])

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Persistence generation with UCRSegments" % (stage,)
    persistence = subprocess.Popen(["python", "-O", "-m", "persistence.PersistenceGenerator", 
                                    "--infile", "%s/%s" % (out_dir, "TimeSeriesSegment.json"),
                                    "--outfile", "%s/%s" % (out_dir, "TimeSeriesPersistence.json"),
                                    "--pool", pool], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = persistence.communicate()

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Kernel generation with UCRSegments" % (stage,)
    subprocess.call(["python", "-O", "-m", "persistence.PersistenceKernel", 
                     "--infile", "%s/%s" % (out_dir, "TimeSeriesPersistence.json"),
                     "--outfile", "%s/%s" % (out_dir, "TimeSeriesKernel.json"),
                     "--pool", pool])

stage = stage + 1
if args.stage == 0 or args.stage == stage :
    print "(stage %s): Testing Learning with UCRSegments" % (stage,)
    subprocess.call(["python", "-O", "-m", "persistence.KernelLearning", 
                     "--infile", "%s/%s" % (out_dir, "TimeSeriesKernel.json"),
                     "--outfile", "%s/%s" % (out_dir, "TimeSeriesLearning.json"),
                     "--pool", pool])

stage = stage + 1
