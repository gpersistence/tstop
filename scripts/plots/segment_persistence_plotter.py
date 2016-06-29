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

from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD
from persistence.PersistenceGenerator import process
from persistence.Datatypes.Segments import Segment, Segments, max_label
from persistence.UCRSegments import UCRSegments
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Configuration import Configuration, parse_index

class CanvasFrame(wx.Frame) :
    def __init__(self, full_data, segment_data, persistences) :
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
        self.colors = [[(random.random(), random.random(), random.random()) for i in self.full_data.config.data_index] 
                       for l in self.labels]
        self.data_figure = Figure()
        self.data_axes = self.data_figure.add_subplot(111)
        self.data_canvas = FigureCanvas(self, -1, self.data_figure)
        self.title = self.data_figure.suptitle("Line %s of %s Label %s" % \
                                               (self.segment_index, len(self.full_data.segments),
                                                self.full_data.segments[self.segment_index].max_label()))
        self.persistence_figure = Figure()
        self.persistence_axes = self.persistence_figure.add_subplot(111)
        self.persistence_canvas = FigureCanvas(self, -1, self.persistence_figure)
        self.persistence_title = self.persistence_figure.suptitle("Persistence Diagram %s of %s window size %s" % \
                                                           (self.segment_index, len(self.full_data.segments),
                                                            self.segment_data.segments[self.segment_index].window_size))
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.sizer.Add(NavigationToolbar2Wx(self.data_canvas), pos=(0,0), span=(1,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(1,0)
        self.sizer.Add(self.data_canvas, pos=(1,0), span=(8,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(9,0)
        self.sizer.Add(self.persistence_canvas, pos=(9,0), span=(8,2), flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.background = self.data_axes.figure.canvas.copy_from_bbox(self.data_axes.bbox)
        self.refresh()

    def refresh(self) :
        while self.full_data.segments[self.segment_index].max_label() != self.labels[self.label_index] :
            self.segment_index = (self.segment_index + 1) % len(self.full_data.segments)
        self.data_canvas.restore_region(self.background)
        self.title.set_text("Line %s of %s Label %s" % \
                            (self.segment_index, len(self.full_data.segments),
                             self.full_data.segments[self.segment_index].max_label()))
        self.data_axes.cla()
        
        for (index,offset) in zip(self.full_data.config.data_index, range(len(self.full_data.config.data_index))) :
            data = [self.full_data.segments[self.segment_index].windows[0][x] \
                    for x in range(offset, 
                                   len(self.full_data.segments[self.segment_index].windows[0]), 
                                   len(self.full_data.config.data_index))]
            self.data_axes.plot(range(self.full_data.segments[self.segment_index].segment_size),
                                data,
                                color = self.colors[self.label_index][offset], linewidth=2.0)
        self.persistence_canvas.restore_region(self.background)
        self.persistence_title.set_text("Persistence Diagram %s of %s window size %s" % \
                                        (self.segment_index, len(self.full_data.segments),
                                         self.segment_data.segments[self.segment_index].window_size))
        self.persistence_axes.cla()

        if self.persistences.diagrams[self.segment_index] == None :
            self.persistences.diagrams[self.segment_index] = \
                process((self.segment_data.segments[self.segment_index], 
                         (self.segment_data.config.max_simplices, None)))

        data = self.persistences.diagrams[self.segment_index].points
        if data != None and len(data) > 0 :
            xs = [d[0] for d in data]
            ys = [d[1] for d in data]
            max_val = max([max(xs),max(ys)])
            self.persistence_axes.scatter(xs,ys)
            self.persistence_axes.plot([0,max_val],[0,max_val],color="red")
        

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
        self.data_canvas.draw()
        self.persistence_canvas.draw()


class App(wx.App):
    def __init__(self, arg, full_data, segment_data, persistences):
        self.full_data = full_data
        self.segment_data = segment_data
        self.persistences = persistences
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.full_data, self.segment_data, self.persistences)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser(description="utility to plot \
    data and dynamically generated persistence diagrams. Using \
    the persistence option uses precomputed persistence and ignores all \
    the other options.")
    parser.add_argument('-i', '--infile', help="Data to read")
    parser.add_argument('-m', '--max-simplices', default=2000000,
                        type=int, help="Maximum number of simplices for persistence \
                        generation")
    parser.add_argument('-I', '--data-index', help="Index of data field for data types that require it")
    parser.add_argument('-L', '--label-index', type=int, help="Index of label field for data types that require it")
    parser.add_argument('-s', '--segment-size', type=int, help="Segment size for data types that require it")
    parser.add_argument('-S', '--segment-stride', type=int, help="Segment stride for data types that require it")
    parser.add_argument('-w', '--window-size', help="Window size for \
    persistence generation. Integer is a literal window size, float \
    between 0 and 1 is a fraction of the total Segment size")
    parser.add_argument('-p', '--persistences', help="Precomputed persistence diagram")
    parser.add_argument('-t', '--data-type', default="UCRSegments", help="Data type of the segments in infile")
    args = parser.parse_args(argv[1:])
    if args.persistences != None :
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
    else :
        segments_module = importlib.import_module( 'persistence.' + args.data_type)    
        segments_class = getattr(segments_module, args.data_type) 
        full_config = Configuration.fromJSONDict(dict([ ("data_type", args.data_type),
                                                        ("data_file", args.infile),
                                                        ("label_index", 0),
                                                        ("max_simplices", args.max_simplices),
                                                        ("window_size", -1),
                                                        ("window_stride", 1)]))
        if full_config.data_file.find(":") != -1 :
            full_config.data_file = full_config.data_file.split(':')
        if args.segment_size != None :
            full_config.segment_size = args.segment_size
        if args.segment_stride != None :
            full_config.segment_stride = args.segment_stride
        if args.data_index != None :
            full_config.data_index = parse_index(args.data_index)[0]
        if args.label_index != None :
            full_config.label_index = args.label_index
        full_data = segments_class(full_config)
        window_size = float(args.window_size)
        if (window_size < 1.0) :
            window_size = int(window_size * full_data.config.window_size)
        else :
            window_size = int(args.window_size)
        window_config =  Configuration.fromJSONDict(dict([ ("data_type", args.data_type),
                                                           ("data_file", full_config.data_file),
                                                           ("label_index", 0),
                                                           ("max_simplices", args.max_simplices),
                                                           ("window_size", window_size),
                                                           ("window_stride", 1)]))
        if args.segment_size != None :
            window_config.segment_size = args.segment_size
        if args.segment_stride != None :
            window_config.segment_stride = args.segment_stride
        if args.data_index != None :
            window_config.data_index = parse_index(args.data_index)[0]
        if args.label_index != None :
            window_config.label_index = args.label_index
        windowed_data = segments_class(window_config)
        persistences = PD(windowed_data.config, [None for segment in windowed_data.segments])
    try:
        app = App(0, full_data, windowed_data, persistences)
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
