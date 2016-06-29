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
import csv
import numpy as np
import matplotlib.pyplot as plt

infile = sys.argv[1]
full_data = []
keys = None
with open(infile, 'rb') as csvfile :
    values = csv.reader(csvfile, delimiter=',')

    for row in values :
        if keys == None:
            keys = [v for v in row if v != '']
        else :
            data = dict(zip(keys, row))
            full_data.append(data)

plot_data = [(data['Dataset'], 
              data['Data Type'],
              float(data['RBF'][0:-1])/100.0            if data['RBF'] != '' else None, 
              float(data['Window Size 10'][0:-1])/100.0 if data['Window Size 10'] != '' else None, 
              float(data['Window Size 20'][0:-1])/100.0 if data['Window Size 20'] != '' else None, 
              float(data['Window Size 30'][0:-1])/100.0 if data['Window Size 30'] != '' else None, 
          ) for data in full_data]


fig = plt.figure()
ax = fig.add_axes([0.1, 0.3, 0.8, 0.65])
plot_data = [p for p in plot_data if p[2] != None and p[3] != None and p[4] != None and p[5] != None]
plot_data.sort(key=(lambda x: "%s %0.2f" % (x[1], max(x[2:]))))
rbf_xs = [x*9   for x in range(len(plot_data))]
pk_xs  = [x*9+3 for x in range(len(plot_data))]
rbf    = [p[2] for p in plot_data]
win = [[], [], []]
for p in plot_data:
    order  = zip(p[3:], [0,1,2])
    order.sort()
    win[order[0][1]].append((0.0, order[0][0]))
    win[order[1][1]].append((order[0][0], order[1][0] - order[0][0]))
    win[order[2][1]].append((order[1][0], order[2][0] - order[1][0]))

plots = []
plots.append(ax.bar(left=rbf_xs, height=rbf, width=3, color="#DB7D2B"))
plots.append(ax.bar(left=pk_xs,  height=[w[1] for w in win[0]], width=3, bottom=[w[0] for w in win[0]], color="#a8ddb5"))
plots.append(ax.bar(left=pk_xs,  height=[w[1] for w in win[1]], width=3, bottom=[w[0] for w in win[1]], color="#7bccc4"))
plots.append(ax.bar(left=pk_xs,  height=[w[1] for w in win[2]], width=3, bottom=[w[0] for w in win[2]], color="#4eb3d3"))
ax.set_ylabel("Accuracy")
ax.set_xticks(pk_xs)
ax.set_xticklabels([p[0] for p in plot_data], rotation=90)
plt.legend(plots, ("RBF Kernel", "Window Size 10", "Window Size 20", "Window Size 30"), ncol=4).draggable()

plt.show()
