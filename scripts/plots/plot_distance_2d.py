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
matplotlib.use('pdf')
matplotlib.rcParams['font.size']=20
matplotlib.rcParams['xtick.labelsize']='small'
matplotlib.rcParams['ytick.labelsize']='small'
import matplotlib.pyplot as plt

labels = dict([('1', 'Working at Computer'),
               ('2', 'Standing Up, Walking, \nGoing Up/Down Stairs'),
               ('3', 'Standing'),
               ('4', 'Walking'),
               ('5', 'Going Up/Down Stairs'),
               ('6', 'Walking and Talking'),
               ('7', 'Talking while Standing')])

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure
from matplotlib.image import AxesImage
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

    def __init__(self, distances) :
        wx.Frame.__init__(self, None, -1, 'Persistence Diagram Distances', size=(900,900))
        self.distances = distances
        self.distances_array = [numpy.asarray([[d.mean for d in row] for row in self.distances[0].distances]),
                                numpy.asarray([[d.mean for d in row] for row in self.distances[1].distances])]
        self.min = min([numpy.min(self.distances_array[0]),numpy.min(self.distances_array[1])])
        self.max = max([numpy.max(self.distances_array[0]),numpy.max(self.distances_array[1])])
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.min = numpy.min(self.distances_array[0]) 
        self.max = numpy.max(self.distances_array[0]) * 0.5
        self.axes_0 = self.figure.add_subplot(121)
        self.axes_0.imshow(self.distances_array[0], vmin=self.min, vmax=self.max, interpolation="nearest",  cmap=plt.get_cmap("coolwarm"))
        self.min = numpy.min(self.distances_array[1])
        self.max = numpy.max(self.distances_array[1]) * 0.5
        self.axes_1 = self.figure.add_subplot(122)
        self.axes_1.imshow(self.distances_array[1], vmin=self.min, vmax=self.max, interpolation="nearest", cmap=plt.get_cmap("coolwarm"))
        
        self.labels = list(set([s.max_label() for s in self.distances[0].segment_info]))
        self.labels.sort()
        self.label_spans = []
        last = 0
        for (s,i) in zip(self.distances[0].segment_info[:-1], range(1,len(self.distances[0].segment_info))) : 
            if s.max_label() != self.distances[0].segment_info[i].max_label() :
                self.label_spans.append((last, i-1, s.max_label()))
                last = i
        self.label_spans.append((last, len(self.distances[0].segment_info), self.distances[0].segment_info[last].max_label()))
        minor_ticks  = [s[0] for s in self.label_spans] + [self.label_spans[-1][1]]
        major_ticks  = [(s[0] + s[1]) / 2.0 for s in self.label_spans]
        major_labels = [s[2] for s in self.label_spans]
        self.axes_0.set_xticks(minor_ticks, minor=True)
        self.axes_0.set_yticks(minor_ticks, minor=True)

        self.axes_0.set_xticks(major_ticks, minor=False)
        self.axes_0.set_xticklabels(major_labels, minor=False, rotation=45, ha='right')
        self.axes_0.set_yticks(major_ticks, minor=False)
        self.axes_0.set_yticklabels(major_labels, minor=False, rotation=45, ha='right')
        self.axes_0.grid(True, which='minor', color='green', linestyle='dashed', linewidth=3.0)
        self.axes_0.set_title("Bottleneck Distances")

        self.axes_1.set_xticks(minor_ticks, minor=True)
        self.axes_1.set_yticks(minor_ticks, minor=True)

        self.axes_1.set_xticks(major_ticks, minor=False)
        self.axes_1.set_xticklabels(major_labels, minor=False, rotation=45, ha='right')
        self.axes_1.set_yticks(major_ticks, minor=False)
        self.axes_1.set_yticklabels(major_labels, minor=False, rotation=45, ha='right')
        self.axes_1.grid(True, which='minor', color='green', linestyle='dashed', linewidth=3.0)
        self.axes_1.set_title("Wasserstein Distances")

        self.segment_info = distances[0].segment_info
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

        self.figure.savefig(self.distances[0].get_distances_filename(self.distances[0].config)[0:-len(".json.gz")]+'.pdf')
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.index = 0
        self.point_Refresh()

    def point_Refresh(self) :
        pass

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
    def __init__(self, arg, distances):
        self.distances = distances
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.distances)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(distances):
    app = App(0, distances)
    app.MainLoop()

def main(argv) :
    current_dir = os.getcwd()
    parser = argparse.ArgumentParser(description="utility to plot distances as a 2-d plot")
    parser.add_argument("-b", "--bottleneck-distances")
    parser.add_argument("-w", "--wasserstein-distances")

    args = parser.parse_args(argv[1:])
    print args.bottleneck_distances
    print args.wasserstein_distances
    distances = [Distances.fromJSONDict(load_data(args.bottleneck_distances, "distances", None, None, argv[0]+": ")),
                 Distances.fromJSONDict(load_data(args.wasserstein_distances, "distances", None, None, argv[0]+": "))]
    segment_info = distances[0].segment_info
    processes = []
    try:
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=(distances,))
        display_thread.start()
        processes.append(display_thread)
        display_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
