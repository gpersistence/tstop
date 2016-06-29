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

from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagram as PD
from persistence.Datatypes.Distances import Distance 
from persistence.PersistenceGenerator import process
from persistence.Datatypes.Segments import Segment, Segments, max_label
from persistence.UCRSegments import UCRSegments
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Configuration import Configuration, parse_index
import math
def format_runtime(runtime) :
    hrs = math.floor(runtime / 3600)
    mns = math.floor(runtime / 60) - hrs * 60
    sec = runtime - hrs * 3600 - mns * 60
    return "%02d:%02d:%02.2f" % (int(hrs), int(mns), sec)

class CanvasFrame(wx.Frame) :
    def __init__(self, full_data) :
        self.full_rips_persistences = [PD.fromJSONDict(entry[0]['full_diagram']) for entry in full_data]
        self.full_rips_runtimes = [format_runtime(entry[0]['runtime']) for entry in full_data]
        self.sparse_rips_persistences = [[PD.fromJSONDict(e['diagram']) for e in entry[1:]] for entry in full_data]
        self.sparse_rips_distances = [[(e['bottleneck_distance'],e['wasserstein_l1'],e['wasserstein_l2']) for e in entry[1:]] \
                                      for entry in full_data]
        self.sparse_rips_sparsity = [[[float(s)*100.0 for s in e['sparsity']] if 'sparsity' in e else None for e in entry[1:]] for entry in full_data]
        self.sparse_rips_runtimes = [[format_runtime(e['runtime']) for e in entry[1:]] for entry in full_data]
        self.simplices = [int(entry['max_simplices']) if 'max_simplices' in entry else None for entry in full_data[0][1:]]
        self.epsilons = [float(entry['epsilon']) if 'epsilon' in entry else None for entry in full_data[0][1:]]

        wx.Frame.__init__(self, None, -1, "Full vs. Sparse Rips Filtration", size=(550, 550))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)

        self.segment_index = 0
        self.full_rips_figure = Figure()
        self.full_rips_axes = self.full_rips_figure.add_subplot(111)
        self.full_rips_canvas = FigureCanvas(self, -1, self.full_rips_figure)
        self.full_rips_title = self.full_rips_figure.suptitle("Persistence Diagram %s of %s runtime %s" % \
                                                              (self.segment_index + 1, len(self.full_rips_persistences), \
                                                               self.full_rips_runtimes[self.segment_index]))

        self.simplices_index = 0
        self.sparse_rips_figure = Figure()
        self.sparse_rips_axes = self.sparse_rips_figure.add_subplot(111)
        self.sparse_rips_canvas = FigureCanvas(self, -1, self.sparse_rips_figure)
        self.sparse_rips_title = self.sparse_rips_figure.suptitle("max simplices %s" % \
                                                                  (self.simplices[self.simplices_index],))

        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.sizer.Add(NavigationToolbar2Wx(self.full_rips_canvas), pos=(0,0), span=(1,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(1,0)
        self.sizer.Add(self.full_rips_canvas, pos=(1,0), span=(8,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(9,0)
        self.sizer.Add(NavigationToolbar2Wx(self.sparse_rips_canvas), pos=(9,0), span=(1,2), flag=wx.EXPAND)
        self.sizer.Add(self.sparse_rips_canvas, pos=(10,0), span=(8,2), flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.background = self.full_rips_axes.figure.canvas.copy_from_bbox(self.full_rips_axes.bbox)
        self.refresh()

    def refresh(self) :
        # Max of all the values so the different plots have the same scale
        max_val = max([max([d[0] for d in self.full_rips_persistences[self.segment_index].points]),
                       max([d[1] for d in self.full_rips_persistences[self.segment_index].points]),
                       max([d[0] for d in self.sparse_rips_persistences[self.segment_index][self.simplices_index].points]),
                       max([d[1] for d in self.sparse_rips_persistences[self.segment_index][self.simplices_index].points])])
                       
        self.full_rips_canvas.restore_region(self.background)
        self.full_rips_title.set_text("Persistence Diagram %s of %s runtime %s" % \
                                        (self.segment_index + 1, len(self.full_rips_persistences), \
                                         self.full_rips_runtimes[self.segment_index]))
        self.full_rips_axes.cla()

        data = self.full_rips_persistences[self.segment_index].points
        if data != None and len(data) > 0 :
            xs = [d[0] for d in data if d[2] == 1]
            ys = [d[1] for d in data if d[2] == 1]
            self.full_rips_axes.scatter(xs,ys, color="blue")
            xs = [d[0] for d in data if d[2] == 0]
            ys = [d[1] for d in data if d[2] == 0]
            self.full_rips_axes.scatter(xs,ys, color="grey")
            self.full_rips_axes.plot([0,max_val],[0,max_val],color="red")

        self.sparse_rips_canvas.restore_region(self.background)
        if self.simplices[self.simplices_index] != None :
            self.sparse_rips_title.set_text("max simplices %s runtime %s sparsity 0 %02.2f%% 1 %02.2f%% 2 %02.2f%%" % \
                                            (self.simplices[self.simplices_index], 
                                             self.sparse_rips_runtimes[self.segment_index][self.simplices_index],
                                             self.sparse_rips_sparsity[self.segment_index][self.simplices_index][0] if self.sparse_rips_sparsity[self.segment_index][self.simplices_index] != None else 0.0,
                                             self.sparse_rips_sparsity[self.segment_index][self.simplices_index][1] if self.sparse_rips_sparsity[self.segment_index][self.simplices_index] != None else 0.0,
                                             self.sparse_rips_sparsity[self.segment_index][self.simplices_index][2] if self.sparse_rips_sparsity[self.segment_index][self.simplices_index] != None else 0.0))
        else :
            self.sparse_rips_title.set_text("epsilon %g runtime %s sparsity 0 %02.2f%% 1 %02.2f%% 2 %02.2f%%" % \
                                            (self.epsilons[self.simplices_index], 
                                             self.sparse_rips_runtimes[self.segment_index][self.simplices_index],
                                             self.sparse_rips_sparsity[self.segment_index][self.simplices_index][0] if self.sparse_rips_sparsity[self.segment_index][self.simplices_index] != None else 0.0,
                                             self.sparse_rips_sparsity[self.segment_index][self.simplices_index][1] if self.sparse_rips_sparsity[self.segment_index][self.simplices_index] != None else 0.0,
                                             self.sparse_rips_sparsity[self.segment_index][self.simplices_index][2] if self.sparse_rips_sparsity[self.segment_index][self.simplices_index] != None else 0.0))
        
        self.sparse_rips_axes.cla()
        self.sparse_rips_axes.set_title("distance bottleneck %.3f wasserstein l1 %.3f l2 %.3f" % \
                                        (self.sparse_rips_distances[self.segment_index][self.simplices_index][0],
                                         self.sparse_rips_distances[self.segment_index][self.simplices_index][1],
                                         self.sparse_rips_distances[self.segment_index][self.simplices_index][2]),
                                        fontdict=dict([('fontsize',12)]))

        data = self.sparse_rips_persistences[self.segment_index][self.simplices_index].points
        if data != None and len(data) > 0 :
            xs = [d[0] for d in data if d[2] == 1]
            ys = [d[1] for d in data if d[2] == 1]
            self.sparse_rips_axes.scatter(xs,ys, color="blue")
            xs = [d[0] for d in data if d[2] == 0]
            ys = [d[1] for d in data if d[2] == 0]
            self.sparse_rips_axes.scatter(xs,ys, color="grey")
            self.sparse_rips_axes.plot([0,max_val],[0,max_val],color="red")
        

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.simplices_index = (self.simplices_index - 1) % len(self.simplices)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            self.simplices_index = (self.simplices_index + 1) % len(self.simplices)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_UP :
            self.segment_index = (self.segment_index - 1) % len(self.full_rips_persistences)            
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_DOWN :
            self.segment_index = (self.segment_index + 1) % len(self.full_rips_persistences) 
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        else :
            pass
        event.Skip()

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.full_rips_canvas.draw()
        self.sparse_rips_canvas.draw()


class App(wx.App):
    def __init__(self, arg, full_data):
        self.full_data = full_data
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.full_data)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

import glob
def main(argv) :
    parser = argparse.ArgumentParser(description="utility to plot \
    persistence diagrams for examining full vs sparse rips filtration")
    parser.add_argument('-p', '--prefix', help="data file prefix (e.g. foo.json to plot foo.json.0000 - foo.json.9999)")
    args = parser.parse_args(argv[1:])
    files = glob.glob(args.prefix + ".[0-9][0-9][0-9][0-9]")
    files.sort()
    full_data = [load_data(fn, None, None, None, argv[0] + " : ") for fn in files]
    try:
        app = App(0, full_data)
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
