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
import argparse
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams.update({'font.size': 22})
from matplotlib.colors import SymLogNorm
from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
from scipy import stats

class func_wrapper:
    def __init__(self, points, positions, X) :
        self.points = points
        self.positions = positions
        self.X = X

    def __call__(self, i) :
        values = np.vstack([[p[0] for point in points[i:i+50] for p in point], [p[1] for point in points[i:i+50] for p in point]])
        kernel = stats.gaussian_kde(values)
        matrix = np.rot90(np.reshape(kernel(self.positions).T, self.X.shape))
        xs,ys = matrix.shape
        for x in range(0,xs):
            for y in range(ys-x,ys) :
                matrix[y,x] = 0.0
        
        print "computed %s" % i
        return (matrix,i,[diagram.segment_info.max_label() for diagram in persistences.diagrams[i:i+50]], xmin, xmax, ymin, ymax)



if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile")
    parser.add_argument("-d", "--degree", type=int)
    
    parser.add_argument("-p", "--pool", default=multiprocessing.cpu_count(), type=int)
    args = parser.parse_args(sys.argv[1:])
    
    persistences = PersistenceDiagrams.fromJSONDict(load_data(args.infile, "persistences", None, None, sys.argv[0] + ": "))
    
    labels = list(set([diagram.segment_info.max_label() for diagram in persistences.diagrams]))
    labels.sort()

    labels = dict([('1', 'Working at Computer'),
                   ('2', 'Standing Up, Walking, Going Up\Down Stairs'),
                   ('3', 'Standing'),
                   ('4', 'Walking'),
                   ('5', 'Going Up\Down Stairs'),
                   ('6', 'Walking and Talking with Someone'),
                   ('7', 'Talking while Standing')])
    # print "Labels: '%s'" % ("', '".join(labels.values()),)

    Zs = []

    points = [[(point[0],point[1]) for point in diagram.points if (args.degree == None or point[2] == args.degree)] \
              for diagram in persistences.diagrams]
    xmin = min([p[0] for point in points for p in point])
    xmax = max([p[0] for point in points for p in point])
    ymin = min([p[1] for point in points for p in point])
    ymax = max([p[1] for point in points for p in point])
    print xmin, xmax, ymin, ymax
    xmin = 0
    xmax = 200 #min(xmax)
    ymin = 0
    ymax = xmax #min(ymax)

    X, Y = np.mgrid[xmin:xmax:200j, ymin:ymax:200j]
    positions = np.vstack([X.ravel(), Y.ravel()])

    func_obj = func_wrapper(points, positions, X)
    pool = multiprocessing.Pool(args.pool)
    talking_range = [i for i in range(len(persistences.diagrams)) 
                     if len([v for (k,v) in persistences.diagrams[i].segment_info.labels.items() if k != '7' and v != 0]) == 0]
    walking_range = [i for i in range(len(persistences.diagrams)) 
                     if len([v for (k,v) in persistences.diagrams[i].segment_info.labels.items() if k != '4' and v != 0]) == 0]
    print min(walking_range), max(walking_range)
    window_size = 50
    Zs = pool.map(func_obj, [talking_range[i] for i in range(0, len(talking_range), window_size)])


    max_val = max([np.max(Z[0]) for Z in Zs])
    max_val = 0.09384
    f = plt.figure()
    
    axes = f.add_axes([0.1, 0.15, 0.7, 0.7])
    cax = f.add_axes([0.8, 0.15, 0.05, 0.8])
    norm = SymLogNorm(1e-5, vmin=0, vmax=max_val)
    for (Z, i, ls, xm1, xm2, ym1, ym2) in Zs :
        im = axes.imshow(Z, extent=[xmin, xmax, ymin, ymax], cmap=plt.get_cmap("hot"), norm=norm) #
        axes.set_xlim([xmin, xmax])
        axes.set_ylim([ymin, ymax])
        axes.plot([xmin, xmax], [xmin, xmax], 'r')
        label = [(l, len([l_ for l_ in ls if l == l_])) for l in list(set(ls))]
        #axes.set_xlabel(", ".join(["%s: %d" % (labels[l[0]],l[1]) for l in label]), fontsize='small')
        axes.set_xlabel("Segments %s to %s" % (i, i+window_size-1), )

        plt.colorbar(im, cax=cax, ticks=[0.0, max_val/1000, max_val/100, max_val/10, max_val])
        

        plt.savefig("%06d.pdf" % i)

