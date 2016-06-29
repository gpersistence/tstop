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


import math
import sys
import csv
import os
import colorsys

import matplotlib.pyplot as plt

if(len(sys.argv) < 3):
    print 'insufficient args'
    sys.exit(1)

window_size = 50
window_stride = 1
segment_size = 1500
segment_stride = 30

activity_file = open(sys.argv[1],'r')
activity_reader = csv.reader(activity_file, delimiter=',')
activity_data = [(float(x[1]),float(x[2]),float(x[3]),x[4]) for x in activity_reader]
x_vals = range(len(activity_data))
unique_activities = set([x[3] for x in activity_data])

print 'list lengths:',len(x_vals),'',len(activity_data)

activities = { '1' : 'Working at Computer' , '2' : 'Standing Up, Walking and Going up down stairs' , '3' : 'Standing' , '4' : 'Walking' , '5' : 'Going up down Stairs' , '6' : 'Walking and Talking with Someone' , '7' : 'Talking while Standing' }

data_dir = sys.argv[2]

for a in unique_activities:
    if a == '0':
        continue
    x_subset = [x for x,d in zip(x_vals,activity_data) if d[3] == a]
    d_subset = [d[0] for d in activity_data if d[3] == a]

    time_series_size = len(d_subset)
    for s in range(0,time_series_size-segment_size, segment_stride):
        segment_filename = data_dir + '/' + activities[a].replace(' ', '_') + '_segment' + '_' + str(s) + '.txt'
        segment_file = open(segment_filename, 'w')
        segment_file.write(str(a) + '\n')
        for t in range(s,(s+segment_size-window_size), window_stride):
            for i in range(t, t+window_size):
                sample = d_subset[i]
                if i < t+window_size-1:
                    segment_file.write(str(sample) + ' ')
                else:
                    segment_file.write(str(sample) + '\n')
        segment_file.close()

all_plots = []
all_labels = []
plt.figure(figsize=(20,10))
for a in unique_activities:
    print 'plotting activity',a
    if a == '0':
        continue
    x_subset = [x for x,d in zip(x_vals,activity_data) if d[3] == a]
    d_subset = [d[0] for d in activity_data if d[3] == a]
    next_plot, = plt.plot(x_subset,d_subset)
    all_plots.append(next_plot)
    all_labels.append(activities[a])
    #plt.plot( [d[2] for d in activity_data] )
    #plt.plot( [d[3] for d in activity_data] )
leg = plt.legend( all_plots, all_labels, loc='upper right', shadow=True)

for legobj in leg.legendHandles:
    legobj.set_linewidth(3.0)

plt.show()
