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
from copy import copy

import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

import wx

from persistence.Datatypes.PersistenceDiagramss import PersistenceDiagrams as PD
from persistence.PersistenceGenerator import process
from persistence.Datatypes.Segments import Segment, Segments, max_label
from persistence.UCRSegments import UCRSegments
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.BottleneckDistance import distance_callable
class CanvasFrame(wx.Frame) :
    def __init__(self, full_data, segment_data, persistences, kNN) :
        self.kNN = kNN
        self.dataset_name = ""
        if isinstance(full_data.config.data_file, list) :
            self.dataset_name = ", ".join([os.path.split(f)[1] for f in full_data.config.data_file])
        else :
            self.dataset_name = os.path.split(full_data.config.data_file)[1]
        wx.Frame.__init__(self, None, -1, self.dataset_name, size=(550, 550))
        self.full_data = full_data
        self.segment_data = segment_data
        self.persistences = persistences
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.label_index = 0
        self.segment_index = 0
        self.labels = list(set([s.max_label() for s in self.full_data.segments]))
        self.colors = dict([(str(l), (random.random(), random.random(), random.random())) for l in self.labels])
        self.figures = []
        for i in range(self.kNN+1) :
            data_figure = Figure()
            data_axes = data_figure.add_subplot(111)
            data_canvas = FigureCanvas(self, -1, data_figure)
            data_title = data_figure.suptitle("Line %s of %s Label %s" % \
                                         (self.segment_index, len(self.full_data.segments),
                                          self.full_data.segments[self.segment_index].max_label()))
            persistence_figure = Figure()
            persistence_axes = persistence_figure.add_subplot(111)
            persistence_canvas = FigureCanvas(self, -1, persistence_figure)
            persistence_title = persistence_figure.suptitle("Persistence Diagram %s of %s window size %s" % \
                                                            (self.segment_index, len(self.full_data.segments),
                                                             self.segment_data.segments[self.segment_index].window_size))
            self.figures.append(dict([("data_figure", data_figure),
                                      ("data_axes", data_axes),
                                      ("data_canvas", data_canvas),
                                      ("data_title", data_title),
                                      ("persistence_figure", persistence_figure),
                                      ("persistence_axes", persistence_axes),
                                      ("persistence_canvas", persistence_canvas),
                                      ("persistence_title", persistence_title)]))
                                      
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        for i in range(self.kNN+1) :
            self.sizer.Add(NavigationToolbar2Wx(self.figures[i]['data_canvas']), pos=(0,(i*2)), span=(1,2), flag=wx.EXPAND)
            self.sizer.Add(self.figures[i]['data_canvas'], pos=(1,(i*2)), span=(8,2), flag=wx.EXPAND)
            self.sizer.Add(self.figures[i]['persistence_canvas'], pos=(9,(i*2)), span=(8,2), flag=wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Fit()
        self.background = self.figures[0]['data_axes'].figure.canvas.copy_from_bbox(self.figures[0]['data_axes'].bbox)
        self.refresh()

    def refresh(self) :
        data_len = len(self.full_data.segments)
        while self.full_data.segments[self.segment_index].max_label() != self.labels[self.label_index] :
            self.segment_index = (self.segment_index + 1) % data_len

        distances = [(i, 
                      distance_callable(1)((self.persistences.persistences[self.segment_index], 
                                           self.persistences.persistences[i])), 
                      self.full_data.segments[i].max_label()) \
                     for i in range(data_len) if i != self.segment_index]
        distances.sort(key=lambda x:x[1].mean)
        print "Bottleneck Distance mean min %s, max %s" % (distances[0][1].mean, distances[-1][1].mean)
        for (f, i) in zip(self.figures, range(self.kNN+1)) :
            f['data_canvas'].restore_region(self.background)
            f['persistence_canvas'].restore_region(self.background)
            f['data_axes'].cla()
            f['persistence_axes'].cla()
            if i == 0 :
                index = self.segment_index
                label = self.full_data.segments[self.segment_index].max_label()
                distance = 0
            else :
                index = distances[i-1][0]
                label = distances[i-1][2]
                distance = distances[i-1][1].mean
            f['data_title'].set_text("Line %s of %s Label %s" % (index, data_len, label))
            f['data_axes'].plot(range(self.full_data.segments[index].segment_size),
                                self.full_data.segments[index].windows[0],
                                color = self.colors[str(label)], linewidth=2.0)
            if i == 0 :
                f['persistence_title'].set_text("Persistence Diagram %s of %s window size %s" % \
                                                (index, data_len, self.segment_data.segments[index].window_size))
            else :
                f['persistence_title'].set_text("Persistence Diagram %s of %s distance %s" % \
                                                (index, data_len, distance))


            data = self.persistences.persistences[index].points
            if data != None and len(data) > 0 :
                xs = [d[0] for d in data]
                ys = [d[1] for d in data]
                max_val = max([max(xs),max(ys)])
                f['persistence_axes'].scatter(xs,ys)
                f['persistence_axes'].plot([0,max_val],[0,max_val],color="red")
        

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.label_index = (self.label_index - 1) % len(self.labels)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            self.label_index = (self.label_index + 1) % len(self.labels)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_UP :
            self.segment_index = (self.segment_index - 1) % len(self.full_data.segments)            
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_DOWN :
            self.segment_index = (self.segment_index + 1) % len(self.full_data.segments)            
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        else :
            pass
        event.Skip()

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        for i in range(self.kNN+1) :
            self.figures[i]['data_canvas'].draw()
            self.figures[i]['persistence_canvas'].draw()


class App(wx.App):
    def __init__(self, arg, full_data, segment_data, persistences, kNN):
        self.full_data = full_data
        self.segment_data = segment_data
        self.persistences = persistences
        self.kNN = kNN
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.full_data, self.segment_data, self.persistences, self.kNN)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser(description="utility to plot data and persistence diagrams. Also plots the 5 \
    nearest neighbors to the selected segment")
    parser.add_argument('-p', '--persistences', help="Precomputed persistence diagram")
    parser.add_argument('-k', '--kNN', default=3, help="number of nearest neighbors to plot")
    args = parser.parse_args(argv[1:])

    persistences_json = load_data(args.persistences, 'persistences', None, None, argv[0])
    if persistences_json == None :
        print "Could not load --persistences : %s" % (args.persistences,)
        exit()
    persistences = PD.fromJSONDict(persistences_json)
    full_config = copy(persistences.config)
    full_config.window_size = -1
    segments_module = importlib.import_module( 'persistence.' + persistences.config.data_type)    
    segments_class = getattr(segments_module, persistences.config.data_type) 

    full_data = segments_class(full_config)
    window_config = copy(persistences.config)
    windowed_data = segments_class(window_config)

    try:
        app = App(0, full_data, windowed_data, persistences, int(args.kNN))
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
