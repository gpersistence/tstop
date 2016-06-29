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
import matplotlib as mpl
mpl.rcParams['font.size']=24
mpl.rcParams['legend.fontsize']=20
import matplotlib.pyplot as plt

from sklearn import manifold

from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Distances import Distances, Distance
from persistence.Datatypes.Learning import Learning, LearningResult

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--learning", nargs="+")
parser.add_argument("-d", "--distance-10")
parser.add_argument("-e", "--distance-20")
parser.add_argument("-f", "--distance-30")

parser.add_argument("-p", "--pool", default=max(1,multiprocessing.cpu_count()-2), type=int)
args = parser.parse_args(sys.argv[1:])
learning = [Learning.fromJSONDict(load_data(l,"learning", None, None, sys.argv[0] + ": ")) for l in args.learning]
distances = [Distances.fromJSONDict(load_data(args.distance_10, "distances", None, None, sys.argv[0] + ": ")),
             Distances.fromJSONDict(load_data(args.distance_20, "distances", None, None, sys.argv[0] + ": ")),
             Distances.fromJSONDict(load_data(args.distance_30, "distances", None, None, sys.argv[0] + ": "))]
filedict = []
f, axes = plt.subplots(2,2)
colors_bright = ['red','green','orange','blue','violet']
colors = ['#d73027','#fc8d59','#fee090','#4575b4', '#91cf60', '#1a9850', '#91bfdb']
values = []
for l,f in zip(learning, args.learning) :
    correct = l.get_average_correct()
    if "PersistenceKernel" in f:
        tags = f.split('-')
        name = "Window Size %s" % (tags[tags.index('win')+1],)
    else :
        name = "RBFKernel"

    values.append((name,correct))
values.sort()
i=0
plots=[]
for name, val in values :
    plots.append(axes[0][0].bar(i*10, val, color=colors[i], width=8))
    i = i + 1
axes[0][0].set_ylim(0.0,0.33,auto=False)
axes[0][0].set_ylabel('Accuracy')
axes[0][0].set_xticks([])
axes[0][0].legend(plots, [name for name,val in values], ncol=2).draggable() 
axes[0][0].set_title("Learning Results")

ax_s = [axes[0][0],axes[0][1],axes[1][0],axes[1][1]]
for d,ax in zip(distances, ax_s[1:]) :
    matrix = np.ndarray((len(d.segment_info),len(d.segment_info)))
    for i in range(len(d.segment_info)) :
        for j in range(i, len(d.segment_info)) :
            matrix[i][j] = d.distances[i][j].mean
            matrix[j][i] = matrix[i][j]

    mds = manifold.MDS(n_components=2, dissimilarity='precomputed', n_jobs=args.pool)

    points = mds.fit_transform(matrix)
    
    labels = [s.max_label() for s in d.segment_info]

    labeled = dict([(label, [p for (p,l) in zip(points, labels) if l == label]) for label in list(set(labels))])

    labels = list(set(labels))
    labels.sort()
    label_ind = dict([(str(l), i) for (l,i) in zip(labels, range(len(labels)))])
    for k,v in labeled.iteritems() :
        xs = [p[0] for p in v]
        ys = [p[1] for p in v]
        ax.scatter(xs,ys,c=colors_bright[(label_ind[str(k)]*4) % len(colors_bright)], linewidth=0, s=50)
    ax.set_title("Window Size %s" % (d.config.window_size))

plt.show()
