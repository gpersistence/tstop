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


#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
import os
import random

with open(sys.argv[1],'r') as plot_file :
    plot_reader = csv.reader(plot_file, delimiter=',')
    full_data = [line for line in plot_reader]
labels = full_data[0]
data = full_data[1:]
t_i = labels.index('Learning Type')
c_i = labels.index('Correct')
w_i = labels.index('Window Size')
types = list(set(d[t_i] for d in data))
data = [(int(d[w_i]),d[t_i],float(d[c_i])) for d in data]

data.sort()
print data
plots = []
width = 0.8
windows = list(set([d[0] for d in data]))
windows.sort()
offset = [0.4 * x for x in range(len(windows))]
for t in types :
    plots.append((t,plt.bar([x + offset[windows.index(data[x][0])] for x in range(len(data)) if data[x][1] == t], 
                            [d[2] * 100.0 for d in data if d[1] == t], width,
                            color=(random.random(), random.random(), random.random()))))

plt.ylabel('Percent Correct')
plt.xlabel('Window Size')
plt.title(sys.argv[1])
tick_labels = list(set([d[0] for d in data]))
tick_labels.sort()
tick_width = [len([d for d in data if d[0] == tick]) for tick in tick_labels]
start = 0
for x in range(len(tick_width)) :
    width = tick_width[x]
    tick_width[x] = start + tick_width[x] / 2.0
    start = start + width + 0.4
plt.xticks(tick_width, tick_labels)
plt.yticks(np.arange(0, 100, 10))
plt.legend([p[1][0] for p in plots], [p[0][0:-len("Learning")] for p in plots], loc="lower right")

plt.show()
