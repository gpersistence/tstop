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
import random
import multiprocessing
import argparse
import importlib
import numpy
import itertools 
from copy import copy
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure
import matplotlib.patches as mpatches

import wx

from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
from persistence.PersistenceGenerator import process
from persistence.Datatypes.Segments import Segment, Segments, max_label
from persistence.UCRSegments import UCRSegments
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.BottleneckDistances import distance_callable
class CanvasFrame(wx.Frame) :
    def __init__(self, params, diagrams, bottleneck_distances, wasserstein_distances) :
        wx.Frame.__init__(self,None,-1,
                         'Bottleneck Distance',size=(550,350))
        self.params = params
        self.diagrams = diagrams
        self.bottleneck_distances = bottleneck_distances
        self.wasserstein_distances = wasserstein_distances

        self.segment_index = 0
        self.segment_start = list(set([p_['segment_start'] for p in self.params for p_ in p]))
        self.segment_start.sort()
        self.segment_sizes = list(set([p_['segment_size'] for p in self.params for p_ in p]))
        self.segment_sizes.sort()
        self.alpha = list(set([float(p_['max_simplices']) / (float(p_['segment_size'])**2) for p in self.params for p_ in p]))
        self.alpha.sort()
        self.runtimes = [(numpy.mean([p_['runtime'] for p in self.params for p_ in p 
                                      if p_['segment_size'] == size and float(p_['max_simplices']) / (float(p_['segment_size'])**2) == alpha]), 
                          size, alpha) for (size, alpha) in itertools.product(self.segment_sizes, self.alpha)]

        d_avg = []
        for i in range(len(self.segment_sizes)) :
            this_distances = [self.bottleneck_distances[j] for j in range(i,len(self.bottleneck_distances),len(self.segment_sizes))]
            d0 = [[[d[j][k] for d in this_distances if d[j][k] != -1] for k in range(len(this_distances[0][0]))] 
                  for j in range(len(this_distances[0]))]
            d0_avg = [[numpy.mean(d0[j][k]) if len(d0[j][k]) != 0 else 0.0 for k in range(len(this_distances[0][0]))] 
                      for j in range(len(this_distances[0]))]
            this_distances = [self.wasserstein_distances[j] for j in range(i,len(self.wasserstein_distances),len(self.segment_sizes))]
            d1 = [[[d[j][k] for d in this_distances if d[j][k] != -1] for k in range(len(this_distances[0][0]))] 
                  for j in range(len(this_distances[0]))]
            d1_avg = [[numpy.mean(d1[j][k]) if len(d1[j][k]) != 0 else 0.0 for k in range(len(this_distances[0][0]))] 
                      for j in range(len(this_distances[0]))]
            d_avg.append((d0_avg, d1_avg))

        self.plot_data = [(d0[0][1:], d1[0][1:]) for (d0, d1) in d_avg]
        
        self.colors = ['#d73027','#fc8d59','#fee090','#4575b4', '#91cf60', '#1a9850', '#91bfdb']
        self.figure = Figure()
        self.axes_bottleneck = self.figure.add_subplot(511)
        self.axes_wasserstein = self.figure.add_subplot(512)
        self.axes_runtime = self.figure.add_subplot(514)
        self.axes_simplices = self.figure.add_subplot(515)
        self.canvas = FigureCanvas(self, -1, self.figure)
        #        self.title = self.figure.suptitle("Ttile")
        self.sizer = self.sizer = wx.BoxSizer(wx.VERTICAL)
        i = 0
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)

        self.SetSizer(self.sizer)
        self.background = self.axes_bottleneck.figure.canvas.copy_from_bbox(self.axes_bottleneck.bbox)
        self.refresh()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)


    def refresh(self) :
        self.canvas.restore_region(self.background)
        self.axes_bottleneck.cla()
        xs = [self.segment_sizes[i] + (8) * (j - 0.5 * float(len(self.alpha)-1)) for i in range(len(self.segment_sizes)) for j in range(len(self.alpha)-1)]
        ys = [p_ for p in self.plot_data for p_ in p[0]]
        colors = [self.colors[j] for p in self.plot_data for j in range(len(p[0]))]
        plots = [self.axes_bottleneck.bar([xs[i] for i in range(j, len(xs), len(self.alpha)-1)], 
                                          [ys[i] for i in range(j, len(xs), len(self.alpha)-1)], width = 7, 
                                          color = self.colors[j]) for j in range(len(self.alpha)-1)]
        self.axes_bottleneck.set_xticks([50] + self.segment_sizes + [500])
        self.axes_bottleneck.set_xticklabels([''] + [str(s) for s in self.segment_sizes] + [''])
        self.axes_bottleneck.set_ylabel("Bottleneck Distance")

        self.axes_wasserstein.cla()
        xs = [self.segment_sizes[i] + (8) * (j - 0.5 * float(len(self.alpha)-1)) for i in range(len(self.segment_sizes)) for j in range(len(self.alpha)-1)]
        ys = [p_ for p in self.plot_data for p_ in p[1]]
        colors = [self.colors[j] for p in self.plot_data for j in range(len(p[1]))]
        plots = [self.axes_wasserstein.bar([xs[i] for i in range(j, len(xs), len(self.alpha)-1)], 
                                           [ys[i] for i in range(j, len(xs), len(self.alpha)-1)], width = 7, 
                                           color = self.colors[j]) for j in range(len(self.alpha)-1)]
        self.axes_wasserstein.set_xticks([50] + self.segment_sizes + [500])
        self.axes_wasserstein.set_xticklabels([''] + [str(s) for s in self.segment_sizes] + [''])
        self.axes_wasserstein.set_ylabel("Wasserstein Distance")

        plots = []
        self.axes_runtime.cla()
        for i in range(len(self.alpha)) :
            color = self.colors[(i-1) % len(self.colors)]
            xs = self.segment_sizes
            ys = [[r[0] for r in self.runtimes if r[1] == size and r[2]==self.alpha[i]][0] for size in self.segment_sizes]
            plots.append(self.axes_runtime.plot(xs,ys, color=color))

        self.axes_runtime.set_xticks([50] + self.segment_sizes + [500])
        self.axes_runtime.set_xticklabels([''] + [str(s) for s in self.segment_sizes] + [''])
        self.axes_runtime.set_ylabel("Seconds")
        self.axes_runtime.set_yscale("log")

        plots = []
        self.axes_simplices.cla()
        for i in range(len(self.alpha)-1) :
            color = self.colors[i]
            xs = self.segment_sizes
            ys = [self.alpha[i+1]*size*size for size in self.segment_sizes]
            plots.append(self.axes_simplices.plot(xs,ys, color=color))
        self.axes_simplices.set_ylabel("Max Simplices")
        self.axes_simplices.set_yscale("log")

        self.axes_simplices.set_xticks([50] + self.segment_sizes + [500])
        self.axes_simplices.set_xticklabels([''] + [str(s) for s in self.segment_sizes] + [''])

        alpha = [str(a) if a > 0 else "Full" for a in self.alpha]

        patches = [mpatches.Patch(color = self.colors[(i-1) % len(self.colors)], 
                                  label = str(self.alpha[i]) if self.alpha[i] > 0 else "Full") 
                   for i in range(len(self.alpha))]

        self.axes_runtime.legend(patches, alpha, loc='best', title="Alpha", ncol=len(self.alpha)).draggable()
        self.axes_simplices.set_xlabel("Segment Size")



        self.Fit()

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
#            self.label_index = (self.label_index - 1) % len(self.labels)
#            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
#            self.label_index = (self.label_index + 1) % len(self.labels)
#            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_UP :
#            self.segment_index = (self.segment_index - 1) % len(self.full_data.segments)            
#            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_DOWN :
#            self.segment_index = (self.segment_index + 1) % len(self.full_data.segments)            
#            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        else :
            pass
        event.Skip()

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()


class App(wx.App):
    def __init__(self, arg, params, diagrams, bottleneck_distances, wasserstein_distances):
        self.params = params
        self.diagrams = diagrams
        self.bottleneck_distances = bottleneck_distances
        self.wasserstein_distances = wasserstein_distances

        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.params, self.diagrams, self.bottleneck_distances,  self.wasserstein_distances)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="Precomputed analysis")

    args = parser.parse_args(argv[1:])

    data_json = load_data(args.input, None, None, None, argv[0]+ ": ")
    if data_json == None :
        print "Could not load --input : %s" % (args.input,)
        exit()

    params    = [ [dict([('segment_start', d['segment_start']),
                         ('segment_size', d['segment_size']),
                         ('max_simplices', d['max_simplices']),
                         ('runtime', d['runtime'])])
                   for d in sample_data[0]]
                  for sample_data in data_json ]

    diagrams  = [ [PersistenceDiagram.fromJSONDict(d['diagram']) for d in sample_data[0]] for sample_data in data_json ]

    bottleneck_distances  = [ [[d['mean'] for d in row] for row in sample_data[1]] \
                              for sample_data in data_json ]
    wasserstein_distances = [ [[d['mean'] for d in row] for row in sample_data[2]] \
                              for sample_data in data_json ]
    try:
        app = App(0, params, diagrams, bottleneck_distances, wasserstein_distances)
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
