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
import matplotlib.animation as animation
from scipy import spatial
import collections

import sys
import csv
import os
import random

if(len(sys.argv) < 2):
    print 'insufficient args'
    sys.exit(1)
base_file = sys.argv[1]

def update_data(num, the_pds, scatter_plot):
    the_pd = the_pds[num]
    #scatter_plot.set_data(the_pds[:,0],the_pds[:,1])
    scatter_plot.set_offsets(the_pds[:,0],the_pds[:,1])

def setup_plot:

data_inds = range(400)
fig = plt.figure()
all_pds = []
first_pd = base_file+'10'+'.txt'
for t in range(10,500):
    pd_filename = base_file+str(t)+'.txt'
    pd_file = open(pd_filename,'r')
    pd_reader = csv.reader(pd_file, delimiter=' ')
    pd = np.array([[float(x[0]),float(x[1])] for x in pd_reader])
    all_pds.append(pd)

#max_pd = max(pd[:,1])
#min_pd = min(pd[:,0])
#plt.scatter(pd[:,0],pd[:,1],color='blue', c=all_densities,s=10)
first_pd = all_pds[0]
fig,ax = plt.subplots()
#l = plt.scatter(first_pd[:,0],first_pd[:,1])
#l, = plt.plot(x=[min_pd,max_pd],y=[min_pd,max_pd])
l_ani = animation.FuncAnimation(fig, update_data, 25, init_func=setup_plot, fargs=(data_inds, l))
