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
import math
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Distances import Distances, Distance
from persistence.Datatypes.Learning import Learning, LearningResult 
from persistence.Datatypes.TrainTestPartitions import TrainTestPartitions, TrainTestPartition

def segment_correctness(index, learning, partition) :
    result = []
    for (l,p) in zip(learning.results, partition.evaluation) :
        if index in p.test :
            i = p.test.index(index)
            result.append(l.test_labels[i] == l.test_results[i])
    if len(result) > 0 :
        return float(len([r for r in result if r == True])) / float(len(result))
    else :
        return None

def average_distance(target_index, dest_label, distances) :
    return numpy.average([distances.distances[target_index][j].mean \
                          for j in range(len(distances.segment_info)) \
                          if distances.segment_info[j].max_label() == dest_label])

class CanvasFrame(wx.Frame):

    def __init__(self, argv):
        wx.Frame.__init__(self,None,-1,
                         'Bottleneck Distance',size=(550,350))
        parser = argparse.ArgumentParser(description="Utility to plot Bottleneck Distance average of 'representative' segments for each label")
        parser.add_argument('-d','--distances')
        parser.add_argument('-l','--learning')
        parser.add_argument('-p','--partition')
        parser.add_argument('-t','--threshold', default=0.75, type=float)
        self.args = parser.parse_args(argv[1:])
        import traceback
        try :
            self.distances = \
              Distances.fromJSONDict(load_data(self.args.distances, 'distances', None, None, argv[0]+": "))
            self.learning = \
              Learning.fromJSONDict(load_data(self.args.learning, 'learning', None, None, argv[0]+": "))
            self.partitions = \
              TrainTestPartitions.fromJSONDict(load_data(self.args.partition, 'partition', None, None, argv[0]+": "))
        except :
            print "Could not parse input files: %s" % (traceback.format_exc(),)
            sys.exit(1)
        
        # Filter to only the segments that get above the threshold
        
        self.segments = []

        for i in range(len(self.distances.segment_info)) :
            c = segment_correctness(i, self.learning, self.partitions)
            if c == None or c > self.args.threshold :
                self.segments.append((i, self.distances.segment_info[i].max_label()))
        sort_format = "0" * int(math.ceil(math.log(len(self.distances.segment_info))))
        self.segments.sort(key=lambda x: str(x[1]+(("%"+sort_format+"d") % x[0])))

        self.label_index = 0
        self.labels = list(set([x[1] for x in self.segments]))
        self.labels.sort()

        self.segment_minimums = dict([(l, min([i for (i,x) in zip(range(len(self.segments)), self.segments) if x[1] == l])) \
                                       for l in self.labels])
        self.segment_maximums = dict([(l, max([i for (i,x) in zip(range(len(self.segments)), self.segments) if x[1] == l])) \
                                       for l in self.labels])

        self.segment_indices = dict([(l, min([i for (i,x) in zip(range(len(self.segments)), self.segments) if x[1] == l], key=lambda x:average_distance(x,l,self.distances))) \
                                       for l in self.labels])

        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['black', 'red', 'yellow', 'orange', 'blue', 'green', 'violet']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)

        self.index = 0
        self.point_Refresh()
        self.Fit()
        self.figure.savefig(self.distances.config.out_directory + "/" + self.distances.config.out_directory.split('/')[-1] + '-win-' + str(self.distances.config.window_size) + '-best-distances.pdf')
        sys.exit(0)


    def point_Refresh(self) :
        self.canvas.restore_region(self.background)
        self.axes.cla()
        plots = []
        for (l,i) in zip(self.labels, range(len(self.labels))) :
            xs = [i + j * (len(self.labels) + 1) for j in range(len(self.labels))]
            ys = [average_distance(self.segments[self.segment_indices[l_]][0], l, self.distances) \
                  for l_ in self.labels]
            plots.append(self.axes.bar(xs, ys, color=self.colors[i % len(self.colors)]))
        self.axes.legend(plots, self.labels, loc='best').draggable()
        self.axes.set_xticks([0.5 * len(self.labels) + j * (len(self.labels) + 1) for j in range(len(self.labels))])
        self.axes.set_xticklabels(["Segment %s ('%s')" % (self.segment_indices[l], l) for l in self.labels])
        self.axes.set_ylabel("Bottleneck Distance")
        self.axes.set_title(self.distances.config.out_directory.split('/')[-1] + " Window Size " + str(self.distances.config.window_size))

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.segment_indices[self.labels[self.label_index]] = max(min(self.segment_indices[self.labels[self.label_index]] - 1,
                                                                          self.segment_maximums[self.labels[self.label_index]]),
                                                                      self.segment_minimums[self.labels[self.label_index]])
	    self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())

        elif keycode == wx.WXK_RIGHT :
            self.segment_indices[self.labels[self.label_index]] = max(min(self.segment_indices[self.labels[self.label_index]] + 1,
                                                                          self.segment_maximums[self.labels[self.label_index]]),
                                                                      self.segment_minimums[self.labels[self.label_index]])
	    self.point_Refresh()
	    wx.PostEvent(self,wx.PaintEvent())

        elif keycode == wx.WXK_UP :
            self.label_index = (self.label_index + 1) % len(self.labels)
	    self.point_Refresh()
	    wx.PostEvent(self,wx.PaintEvent())

        elif keycode == wx.WXK_DOWN :
            self.label_index = (self.label_index - 1) % len(self.labels)
	    self.point_Refresh()
	    wx.PostEvent(self,wx.PaintEvent())

        else :
            event.Skip()
            
    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()

class App(wx.App):
    def __init__(self, arg, argv):
        self.argv = argv
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.argv)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(argv):
    app = App(0, argv)
    app.MainLoop()

def main(argv) :
    current_dir = os.getcwd()

    processes = []
    try:
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=(argv,))
        display_thread.start()
        processes.append(display_thread)
        display_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
