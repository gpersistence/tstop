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
import numpy as np

if(len(sys.argv) < 2):
    print 'insufficient args'
    sys.exit(1)

time_series_file = open(sys.argv[1],'r')
time_series_reader = csv.reader(time_series_file, delimiter=' ')
all_vals = np.array([[x[0],x[1]] for x in time_series_reader])
plt.figure(figsize=(20,10))
plt.plot(all_vals[:,1])
plt.show()
