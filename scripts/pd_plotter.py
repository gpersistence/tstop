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
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial
import collections

import sys
import csv
import os
import random

if(len(sys.argv) < 2):
    print 'insufficient args'
    sys.exit(1)

pd_file = open(sys.argv[1],'r')
pd_reader = csv.reader(pd_file, delimiter=' ')
pd = np.array([[float(x[0]),float(x[1])] for x in pd_reader])

kd_tree = spatial.cKDTree(pd, 15)

ave_r = 0
the_k = 12
for pt in pd:
    neighbor_dists,neighbor_idx = kd_tree.query(pt, the_k)
    ave_r += neighbor_dists[the_k-1]
ave_r /= len(pd)

scale_r = 1.1
sigma = ave_r*scale_r
query_r = 2.5*sigma

all_neighbors = [kd_tree.query_ball_point(pt,query_r) for pt in pd]

all_densities = [];
for i in range(len(all_neighbors)):
    pt = pd[i]
    density = 0
    if pt[1]-pt[0] < 2e-1:
        all_densities.append(0)
        continue
    print 'pd:',pt
    for k in all_neighbors[i]:
        neighbor_pt = pd[k]
        diff_pt = neighbor_pt-pt
        sqd_dist = diff_pt[0]*diff_pt[0]+diff_pt[1]*diff_pt[1]
        density += math.exp(-sqd_dist/(sigma*sigma))
        #density += -sqd_dist/(sigma*sigma)
    all_densities.append(density)

fig = plt.figure()
max_pd = max(pd[:,1])
min_pd = min(pd[:,0])
#print 'pd bounds:',min_pd,max_pd
#print 'densities:',all_densities
plt.scatter(pd[:,0],pd[:,1],color='blue', c=all_densities,s=10)
plt.colorbar()
#plt.plot([min_pd,max_pd],[min_pd,max_pd],color='black')
plt.plot(x=[min_pd,max_pd],y=[min_pd,max_pd])
plt.show()
