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


import subprocess
import time
import sys
import os
import re
from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Configuration import Configuration, parse_range
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams
from persistence.Datatypes.TrainTestPartitions import TrainTestPartitions
from persistence.UCRSegments import UCRSegments
from persistence.ScaleSpaceSimilarity import ScaleSpaceSimilarity
from persistence.PersistenceKernel import PersistenceKernel
from persistence.RBFKernel import RBFKernel
from persistence.EuclideanDistances import EuclideanDistances
from persistence.DistanceLearning import DistanceLearning
from persistence.KernelLearning import KernelLearning

outputs = []
hosts = dict(#[("name-%s" % i,    ("ip-address", number of threads in a pool)) for i in range(number of processes)] +
             [("localhost-%s" % i,    ("127.0.0.1",  1)) for i in range(4)] + 
             []
)
in_progress = dict([(key, None) for key in hosts.keys()])

# for example, get all segment files in a directory and generate persistence
Segments = subprocess.check_output(["find", "~/2016-02-17-UCR2015", "-name", "*Segments.json.gz"])
Segments = [k.strip() for k in Segments.split()]
Segments.sort()

# a list of python command lines to pass to Popen
tasks = [["python", "-m", "persistence.PersistenceGenerator", "--infile", s] for s in Segments]

output_re = re.compile("^Writing\s+(\S+\.json(\.gz)?)")

done = []
index = 0
while len(tasks) > len(done) :
    one_done = False
    target = None
    while not one_done :
        for key in in_progress.keys() :
            # check to see if a process is complete
            if in_progress[key] == None or in_progress[key][0].poll() != None :
                if in_progress[key] != None :
                    (out,err) = in_progress[key][0].communicate()
                    if err != '' :
                        print "ERROR: " + str(in_progress[key][1]) + " : " + err
                    else :
                        out_files = []
                        for line in out.split() :
                            m = output_re.match(line)
                            if m != None :
                                out_files.append(m.group(1))
                        outputs.extend(out_files)
                        for f in out_files :
                            
                    done.append(in_progress[key][1])
                    in_progress[key] = None
                # mark that we've found a completed process
                one_done = True
                # set the target for the next process
                if target == None :
                    target = key

        if not one_done :
            # wait ten seconds before checking again
            time.sleep(10)

    if index < len(tasks)  :
        # Configure with your LD_LIBRARY_PATH and PYTHONPATH
        p_cmd = ['ssh', hosts[target][0], "LD_LIBRARY_PATH=.:", "PYTHONPATH=.:"] + tasks[index] + ["--pool", str(hosts[target][1])]
        # Check to see if there's a None value in the queue (probably an uncaught error)
        if reduce(lambda x, y: x and y != None, p_cmd, True) :
            print " ".join(p_cmd)
            # Uncomment the following line and comment out the Popen for debugging
            # done.append(tasks[index])
            in_progress[target] = (subprocess.Popen(p_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE), tasks[index])
        else :
            print "Skipping %s" % tasks[index]
            done.append(tasks[index])
        time.sleep(1)
        index = index + 1

# Wait for the rest of the processes to finish
for key in in_progress.keys() :
    if in_progress[key] != None :
        in_progress[key][0].wait()
