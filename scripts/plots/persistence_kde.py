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
from matplotlib.colors import SymLogNorm
from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
from scipy import stats

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
print "Labels: '%s'" % ("', '".join(labels.values()),)
xmin = []
xmax = []
ymin = []
ymax = []
points_list = []
Zs = []
for label in (labels) :
    points = [(point[0],point[1]) for diagram in persistences.diagrams if (label == None or diagram.segment_info.max_label() == label) \
              for point in diagram.points if (args.degree == None or point[2] == args.degree)  ]
    xmin.append(min([p[0] for p in points]))
    xmax.append(max([p[0] for p in points]))
    ymin.append(min([p[1] for p in points]))
    ymax.append(max([p[1] for p in points]))
    points_list.append((points,labels[label]))

xmin = 0
xmax = 200 #min(xmax)
ymin = 0
ymax = xmax #min(ymax)
X, Y = np.mgrid[xmin:xmax:200j, ymin:ymax:200j]
positions = np.vstack([X.ravel(), Y.ravel()])

for points in points_list:
    values = np.vstack([[p[0] for p in points[0]], [p[1] for p in points[0]]])
    kernel = stats.gaussian_kde(values)
    matrix = np.rot90(np.reshape(kernel(positions).T, X.shape))
    xs,ys = matrix.shape
    for x in range(0,xs):
        for y in range(ys-x,ys) :
            matrix[y,x] = 0.0
    Zs.append((matrix,points[1]))
    print "computed %s" % points[1]


max_val = max([np.max(Z[0]) for Z in Zs])

f = plt.figure()

axes = [f.add_axes([0.05 + 0.225 * i, 0.525, 0.175, 0.425]) for i in range(4)] + \
       [f.add_axes([0.05 + 0.225 * i, 0.05, 0.175, 0.425]) for i in range(3)]
#caxes= [f.add_axes([0.05 + 0.175 + 0.225 * i, 0.55, 0.025, 0.4]) for i in range(4)] + \
#       [f.add_axes([0.1625 + 0.175 + 0.225 * i, 0.1, 0.025, 0.4]) for i in range(3)]
norm = SymLogNorm(1e-5, vmin=0, vmax=0.09384)
for (ax,Z) in zip(axes,Zs) :
    im = ax.imshow(Z[0], extent=[xmin, xmax, ymin, ymax], cmap=plt.get_cmap("hot"), norm=norm) #
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.plot([xmin, xmax], [xmin, xmax], 'r')
    if Z[1] != None :
        ax.set_title(Z[1])
    else :
        ax.set_title("All Labels")
cax = f.add_axes([0.16 + 0.225 * 3, 0.05125, 0.05, 0.4])
plt.colorbar(im, cax=cax, ticks=[0.0, max_val/1000, max_val/100, max_val/10, max_val])

#cax = f.add_axes([0.9, 0.1, 0.03, 0.8])
plt.show()

