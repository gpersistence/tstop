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


import subprocess
import argparse
import threading
import multiprocessing
import itertools
import traceback
import os
import os.path
import errno
import sys
import time
import json
import numpy
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx

from persistence import py_persistence

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Segments import Segment, Segments, SegmentInfo
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams
from persistence import PersistenceGenerator
from persistence.Datatypes.Distances import Distances, Distance
from persistence.BottleneckDistances import BottleneckDistances
from persistence.WassersteinDistances import WassersteinDistances

class CanvasFrame(wx.Frame):

    def __init__(self, distance_type, distance_array, segment_compare, segment_info):
        wx.Frame.__init__(self,None,-1,
                         'Persistence Diagram %s Distance' % distance_type, size=(1920,550))
        self.distance_type = distance_type
        self.distance_array = distance_array
        self.xs = range(len(self.distance_array))
        self.timer = wx.Timer(self)
        self.timer.Start(100) # poll every second
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.segment_info = segment_info
        self.index = segment_compare
        self.axes.set_title("Segment %s file %s start %s label %s" % (self.index.value, 
                                                                      self.segment_info[self.index.value].filename, 
                                                                      self.segment_info[self.index.value].segment_start, 
                                                                      self.segment_info[self.index.value].max_label()))
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['black', 'red', 'yellow', 'orange', 'blue', 'green', 'violet']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.Bind(wx.EVT_TIMER, self.TimeEvent, self.timer)
        self.index = segment_compare
        self.point_Refresh()

    def point_Refresh(self) :
        lines = [] 
        self.canvas.restore_region(self.background)
        self.axes.cla()
        self.axes.set_title("Segment %s file %s start %s label %s" % (self.index.value, 
                                                                      self.segment_info[self.index.value].filename, 
                                                                      self.segment_info[self.index.value].segment_start, 
                                                                      self.segment_info[self.index.value].max_label()))
        xs_0 = [i for i in self.xs if self.distance_array[i] >= 0.0] + [len(self.xs)]
        ys_0 = [self.distance_array[i] for i in self.xs if self.distance_array[i] >= 0.0] + [0.0]
        line = self.axes.plot(xs_0, ys_0, 'b')
        lines.append(line)
        max_val = max(ys_0)
        line = self.axes.plot([self.index.value, self.index.value], [0,max_val], 'r')
        lines.append(line)


    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.index.value = (self.index.value - 1) % len(self.distance_array)
	    self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            self.index.value = (self.index.value + 1) % len(self.distance_array)
	    self.point_Refresh()
	    wx.PostEvent(self,wx.PaintEvent())
        else :
            event.Skip()
            
    def TimeEvent(self, event) :
        self.point_Refresh()
        wx.PostEvent(self,wx.PaintEvent())

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()

class App(wx.App):
    def __init__(self, arg, distance_type, distance_array, segment_compare, segment_info):
        self.distance_type = distance_type
        self.distance_array = distance_array
        self.segment_compare = segment_compare
        self.segment_info = segment_info
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.distance_type, self.distance_array, self.segment_compare, self.segment_info)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(distance_type, distance_array, segment_compare, segment_info):
    app = App(0, distance_type, distance_array, segment_compare, segment_info)
    app.MainLoop()

class yieldPersistenceDiagramAndDistance:
    def __init__(self, max_simplices, epsilon, reference, distance_type) :
        self.max_simplices = max_simplices
        self.epsilon = epsilon
        self.reference = reference
        self.distance_type = distance_type

    def __call__(self, (segment, i)) :
        print "starting diagram %s" % (i,)
        diagram = PersistenceGenerator.process((segment, (self.max_simplices, self.epsilon)))
        if self.reference != None:
            if self.distance_type == "bottleneck" :
                distance = py_persistence.bottleneck_distance(self.reference.points, diagram.points, 1)
            elif self.distance_type == "wasserstein" :
                distance = py_persistence.wasserstein_distance(self.reference.points, diagram.points, 1, 2)
            else :
                print "%s is not a valid distance type, exiting" % (self.distance_type,)
                sys.exit(1)
        else :
            distance = 0.0
        print "calculated diagram %s, distance %s" % (i, distance)
        return (i, diagram, distance)

class yieldDistance: 
    def __init__(self, distance_type) :
        self.distance_type = distance_type

    def __call__(self, ((diagram_a, i), (diagram_b, j))) :
        if self.distance_type == "bottleneck" :
            distance = py_persistence.bottleneck_distance(diagram_a.points, diagram_b.points, 1)
        elif self.distance_type == "wasserstein" :
            distance = py_persistence.wasserstein_distance(diagram_a.points, diagram_b.points, 1, 2)
        else :
            print "%s is not a valid distance type, exiting" % (self.distance_type,)
            sys.exit(1)
        return (i, j, distance)

def compute(distance_type, distance_array, segment_compare, pool, max_simplices, epsilon, segments=None, pds=None, ds=None) :
    compute_pool = multiprocessing.Pool(pool)
    d_len = len(distance_array)
    d_rng = range(d_len)
    last = -1
    if pds == None and ds == None:
        persistence_diagrams = [None for x in segments.segments]
        print "Generating initial persistence diagram"
        persistence_diagrams[0] = PersistenceGenerator.process((segments.segments[0], (max_simplices, epsilon)))
        diagram_generator = yieldPersistenceDiagramAndDistance(max_simplices, epsilon, persistence_diagrams[0], distance_type)
        results = compute_pool.imap(diagram_generator, itertools.izip(segments.segments[1:], d_rng[1:]))
        for (i, diagram, distance) in results :
            persistence_diagrams[i] = diagram
            distance_array[i] = distance

        config = segments.config
        config.max_simplices = max_simplices
        config.persistence_epsilon = epsilon
        diagrams = PersistenceDiagrams(config, persistence_diagrams)
        filename = PersistenceDiagrams.get_persistence_diagrams_filename(config)
        print "plot_persistence_distance.py: Writing %s" % (filename,)
        save_data(filename, diagrams.toJSONDict())
    elif pds != None :
        persistence_diagrams = pds.diagrams
        config = pds.config

    distances = [[None for y in d_rng] for x in d_rng]
    if ds == None :
        print "Computing Distance Array"
        distance_generator = yieldDistance(distance_type)
        results = compute_pool.imap(distance_generator, 
                                    itertools.product(itertools.izip(persistence_diagrams, d_rng),
                                                      itertools.izip(persistence_diagrams, d_rng)),
                                    max(1, d_len**2 / (10*pool)))
        for (i, j, distance) in results :
            distances[i][j] = Distance(None, distance, None, None)
            if segment_compare.value != last :
                last = segment_compare.value
                for k in d_rng :
                    distance_array[k] = distances[last][k].mean if distances[last][k] != None else -1.0

        if distance_type == 'bottleneck' :
            filename = BottleneckDistances.get_distances_filename(config)
        elif distance_type == 'wasserstein' :
            filename = WassersteinDistances.get_distances_filename(config)
    
        print "plot_persistence_distance.py: Writing %s" % (filename,)
        save_data(filename, Distances(config, distances, [d.segment_info for d in persistence_diagrams]).toJSONDict())
    else :
        for i in d_rng :
            for j in d_rng :
                distances[i][j] = ds.distances[i][j]
        last = -1
    compute_pool.close()
    compute_pool.join()
    last = segment_compare.value
    for k in d_rng :
        distance_array[k] = distances[last][k].mean
    while True: 
        if segment_compare.value != last :
            last = segment_compare.value
            for k in d_rng :
                distance_array[k] = distances[last][k].mean
        else :
            time.sleep(0.05)


def main(argv) :
    current_dir = os.getcwd()
    parser = argparse.ArgumentParser(description="utility to plot distance persistence diagram")
    parser.add_argument("-s", "--segments")
    parser.add_argument("-P", "--persistence-diagrams")
    parser.add_argument("-d", "--distances")

    parser.add_argument("-t", "--distance-type", default="bottleneck", help="Distance Measure to use, Bottleneck or Wasserstein")
    parser.add_argument("-p", "--pool", default=max(2,multiprocessing.cpu_count()-4), help="Threads of computation to use", type=int)
    parser.add_argument("-m", "--max-simplices", default=1000000, type=int)
    parser.add_argument("-e", "--epsilon", type=float)

    args = parser.parse_args(argv[1:])

    if args.segments != None :
        segments = Segments.fromJSONDict(load_data(args.segments, "segments", None, None, argv[0]+": "))
        segment_info = [SegmentInfo.fromJSONDict(s) for s in segments.segments]
    else :
        segments = None
    if args.persistence_diagrams != None :
        diagrams = PersistenceDiagrams.fromJSONDict(load_data(args.persistence_diagrams, "persistence diagrams", None, None, argv[0]+": "))
        segment_info = [d.segment_info for d in diagrams.diagrams]
    else :
        diagrams = None
    if args.distances != None :
        distances = Distances.fromJSONDict(load_data(args.distances, "distances", None, None, argv[0]+": "))
        segment_info = distances.segment_info
    else :
        distances = None

    distance_array = multiprocessing.Array('d', [0.0] + [-1.0 for s in segment_info[1:]])
    segment_compare = multiprocessing.Value('i', 0)
    processes = []
    try:
        compute_thread = \
          multiprocessing.Process(target=compute,
                                  args=(args.distance_type, distance_array, segment_compare, args.pool-1, 
                                        args.max_simplices, args.epsilon, segments, diagrams, distances))
        compute_thread.start()
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=(args.distance_type, distance_array, segment_compare, segment_info))
        display_thread.start()
        processes.append(display_thread)
        display_thread.join()
        compute_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
