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
from copy import copy
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('pdf')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx

from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
from persistence.PersistenceGenerator import process
from persistence.Datatypes.Distances import Distances
from persistence.UCRSegments import UCRSegments
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.BottleneckDistances import distance_callable
class CanvasFrame(wx.Frame) :
    def __init__(self, distances) :
        wx.Frame.__init__(self,None,-1,
                         'Bottleneck Distance',size=(550,350))
        self.distances = distances
        self.data_name = self.distances.config.out_directory.split('/')[-1]
        self.segment_info = distances.segment_info
        self.labels = list(set([s.max_label() for s in self.segment_info]))
        self.labels.sort()
        print self.labels
        self.data = [(self.segment_info[i].max_label(), i, [numpy.mean([distances.distances[i][j].mean 
                                                                        for j in range(len(self.segment_info)) 
                                                                        if self.segment_info[j].max_label() == label]) 
                                                            for label in self.labels]) 
                     for i in range(len(self.segment_info))]
        self.data.sort()
        self.data_len = [len([d for d in self.data if d[0] == l]) for l in self.labels]
        self.colors = [(random.random(), random.random(), random.random()) for s in self.labels]
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.title = self.figure.suptitle(self.data_name + " Window Size " + str(self.distances.config.window_size))
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), pos=(0,0), span=(1,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(1,0)
        self.sizer.Add(self.canvas, pos=(1,0), span=(8,2), flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.refresh()
        self.figure.savefig(self.data_name+'-'+str(self.distances.config.window_size)+'-distance-labels.pdf')

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)


    def refresh(self) :
        self.canvas.restore_region(self.background)
        self.axes.cla()
        plots = []
        for i in range(len(self.labels)) :
            plot, = self.axes.plot(range(len(self.segment_info)),
                                   [d[2][i] for d in self.data],
                                   color = self.colors[i]) 
            plots.append(plot)

        boundaries = [sum(self.data_len[0:i]) for i in range(len(self.data_len))] + [len(self.segment_info)]
        
        self.axes.set_xticks([(r + l)  / 2.0 for (r,l) in zip(boundaries[0:-1], boundaries[1:])], minor = True)
        self.axes.set_xticklabels(self.labels, minor = True)
        self.axes.set_xticks(boundaries, minor = False)
        self.axes.set_xticklabels(boundaries, minor = False, size = 0)
        self.axes.grid(True, axis='x', which='major')
        self.axes.legend(plots, self.labels, loc='best', title="Labels").draggable()
        self.axes.set_ylabel("Bottleneck Distance")
        self.axes.set_xlabel("Segment Label")
        self.axes.set_xbound(lower=0, upper=len(self.segment_info))

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
    def __init__(self, arg, distances):
        self.distances = distances

        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.distances)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--distances')

    args = parser.parse_args(argv[1:])

    data_json = load_data(args.distances, "distances" , None, None, argv[0]+": ")
    distances = Distances.fromJSONDict(data_json)
    if data_json == None :
        print "Could not load --distances : %s" % (args.distances,)
        exit()

    try:
        app = App(0, distances)
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
