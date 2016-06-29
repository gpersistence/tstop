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


import os
import sys
import argparse
import random
import math
import matplotlib.pyplot as plt
from collections import deque
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

import wx

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD



class CanvasFrame(wx.Frame) :
    def __init__(self, persistences, degree) :
        wx.Frame.__init__(self, None, -1, "Persistence Diagram Density Viewer", 
                          size=(1500,1500))
        self.persistences = persistences
        labels = list(set([d.segment_info.max_label() for d in self.persistences.diagrams]))

        if len(labels) == 1 :
            self.label = labels[0]
        else :
            self.label = None

        self.color = (random.random(), random.random(), random.random())
        self.degree = degree
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.title = self.figure.suptitle("Persistence Diagram Density" + ((" Label '%s'" % self.label) if self.label != None else ""))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), pos=(0,0), 
                       span=(1,2), flag=wx.EXPAND)
        self.sizer.Add(self.canvas, pos=(1,0), span=(8,2), flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.background = \
            self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.refresh()
        points = [(point[0],point[1]) for diagram in self.persistences.diagrams \
                  for point in diagram.points if self.degree == None or point[2] == self.degree ]
        self.max_val = max(max(points, key=lambda x : max(x)))
        self.density_graph = [[0 for x in range(100)] for y in range(100)]
        self.extents = [float(i) * self.max_val / 100.0 for i in range(100)]
        for point in points :
            x = 0
            while point[0] > self.extents[x] and x < 99 :
                x = x + 1
            y = 0
            while point[1] > self.extents[y] and y < 99 :
                y = y + 1
            self.density_graph[y][x] = self.density_graph[y][x] + 1
        self.canvas.restore_region(self.background)
        
        self.axes.cla()
        self.axes.imshow(self.density_graph, vmin=0, vmax=self.max_val, origin='lower',interpolation="nearest")
        num_ticks = len(self.axes.get_xticks())
        
        self.axes.set_xticklabels(["%0.2f" % (self.extents[int(i*100.0/num_ticks)],) for i in range(num_ticks)])
        self.axes.set_yticklabels(["%0.2f" % (self.extents[int(i*100.0/num_ticks)],) for i in range(num_ticks)])

    def refresh(self) :
        pass

    def KeyEvent(self, event) :
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            pass
        elif keycode == wx.WXK_RIGHT :
            pass
        elif keycode == wx.WXK_UP :
            pass
        elif keycode == wx.WXK_DOWN :
            pass
        else :
            pass
        event.Skip()

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()


class App(wx.App):
    def __init__(self, arg, persistence, degree):
        self.persistence = persistence
        self.degree = degree
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.persistence, 
                            self.degree)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser(description="utility to plot \
    the density of all persistence diagrams in a file.")
    parser.add_argument("-i", "--infile")    
    parser.add_argument("-d", "--degree", type=int)
    parser.add_argument("-l", "--label", help="Show only persistence diagrams of a particular label")
    args = parser.parse_args(argv[1:])
    if args.infile == None or not os.path.isfile(args.infile) :
        print "%s : --infile (%s) must specify file that exists" % \
            (argv[0], args.infile)
        sys.exit(0)

    persistence_json = load_data(args.infile, "persistence_diagrams", None, None, argv[0] + " : ")
    if persistence_json == None :
        print "Could not load --infile : %s" % (args.persistence_a,)
        exit()
    persistence = PD.fromJSONDict(persistence_json)
    labels = list(set([d.segment_info.max_label() for d in persistence.diagrams]))
    labels.sort()
    if args.label != None :
        diagrams = [d for d in persistence.diagrams if d.segment_info.max_label() == args.label]
        persistence.diagrams = diagrams
    else :
        print "Labels : %s" % labels

    try:
        app = App(0, 
                  persistence, 
                  args.degree)
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
