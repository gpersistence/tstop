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


import os
import sys
import math
import itertools
import multiprocessing

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
def avg(l) :
    return sum(l,0.0) / len(l)
def average_density(diagram) :
    points = [(p[0], p[1]) for p in diagram.points if p[2] == 1]
    if len(points) > 2 :
        diagram_distances = []
        for (x0,y0) in points :
            distances = map(lambda (x1,y1) : math.sqrt((x0 - x1) * (x0 - x1) + (x0 - x1) * (x0 - x1)), points)
            diagram_distances.append(avg(distances[1:6]))
        return avg(diagram_distances)
    else :
        return 0.0



if __name__ == "__main__" :
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 2)
    for f in sys.argv[1:] :
        pds = PersistenceDiagrams.fromJSONDict(load_data(f, None, None, None, sys.argv[0] + " : "))
        densities = pool.map(average_density, pds.diagrams)
        save_data(f + "-density", list(densities))
