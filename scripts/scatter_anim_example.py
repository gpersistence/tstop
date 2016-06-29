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


import matplotlib.pyplot as plt

import sys
import csv
import os
import random

plt.ion()
class DynamicUpdate():
    #Suppose we know the x range
    min_x = 4
    max_x = 6.5

    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots(2)
        self.pd_plotter, = self.ax[0].plot([],[], 'o')
        self.ts_plotter, = self.ax[1].plot([2], 'r-')
        #Autoscale on unknown axis and known lims on the other
        #self.ax.set_autoscaley_on(True)
        self.ax[0].set_xlim(self.min_x, self.max_x)
        self.ax[0].set_ylim(self.min_x, self.max_x)
        self.ax[1].set_autoscaley_on(True)
        self.ax[1].set_autoscalex_on(True)
        #Other stuff
        #self.ax.grid()
        #...

    def on_running(self, xdata, ydata, ts_data_x, ts_data_y):
        #Update data (with the new _and_ the old points)
        self.pd_plotter.set_xdata(xdata)
        self.pd_plotter.set_ydata(ydata)
        self.ts_plotter.set_xdata(ts_data_x[len(ts_data_x)-1])
        self.ts_plotter.set_ydata(ts_data_y[len(ts_data_y)-1])
        #Need both of these in order to rescale
        self.ax[1].relim()
        self.ax[1].autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def __call__(self):
        import numpy as np
        import time
        self.on_launch()
        base_file = '../build/pd-'
        first_pd = base_file+'10'+'.txt'
        ts_filename = '../build/time_series.txt'
        time_series_file = open(ts_filename,'r')
        time_series_reader = csv.reader(time_series_file, delimiter=' ')
        all_ts_vals = np.array([[x[0],x[1]] for x in time_series_reader])
        for t in range(10,40000):
            pd_filename = base_file+str(t)+'.txt'
            pd_file = open(pd_filename,'r')
            pd_reader = csv.reader(pd_file, delimiter=' ')
            pd = np.array([[float(x[0]),float(x[1])] for x in pd_reader if not (float(x[0]) == float(x[1]))])
            ts_vals_x = all_ts_vals[10:t+1,0]
            ts_vals_y = all_ts_vals[10:t+1,1]
            self.on_running(pd[:,0], pd[:,1], ts_vals_x,ts_vals_y)
            #time.sleep(0.01)
        return xdata, ydata

d = DynamicUpdate()
d()
