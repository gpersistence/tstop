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

from persistence import py_persistence

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams



class CanvasFrame(wx.Frame) :
    def __init__(self, persistence_a, persistence_b, degree, 
                 index_a=None, index_b=None) :
        wx.Frame.__init__(self, None, -1, "Bottleneck Distance Viewer", 
                          size=(1500,1500))
        self.persistence_a = persistence_a
        self.persistence_b = persistence_b
        #self.color_a = (random.random(), random.random(), random.random())
        #self.color_b = (random.random(), random.random(), random.random())
        self.color_a = (1,0,0)
        self.color_b = (0,0,1)
        self.degree = degree
        self.a_index = 0 if index_a == None else index_a
        self.b_index = 0 if index_b == None else index_b
        print "Using A %s and B %s" % (self.a_index, self.b_index)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.title = self.figure.suptitle(("Persistence Diagram A index %d vs " +
                                           "Persistence Diagram B index %d") % \
                                          ( self.a_index, self.b_index ))
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
        


    def refresh(self) :
        self.canvas.restore_region(self.background)
        self.title.set_text(("Persistence Diagram A index %d vs " +
                             "Persistence Diagram B index %d") % \
                            ( self.a_index, self.b_index ))
        points_a = [(point[0],point[1]) \
                    for point in self.persistence_a[self.a_index].points \
                    if point[2] == self.degree]
        points_b = [(point[0], point[1]) \
                    for point in self.persistence_b[self.b_index].points \
                    if point[2] == self.degree]
        print "A[%s] has %s points, B[%s] has %s points" % \
            (self.a_index, len(points_a), self.b_index, len(points_b))
        # returns a list of tuples ((birth, death), (birth, death), distance)
        matches = py_persistence.match_points(self.persistence_a[self.a_index].points, 
                                              self.persistence_b[self.b_index].points, self.degree)
        lines = []
        for ((p0x,p0y),(p1x,p1y),dist) in matches :
            lines.extend([(p0x,p1x),(p0y,p1y),'g'])

        self.axes.cla()
        xs = [p[0] for p in points_a] + [p[0] for p in points_b]
        ys = [p[1] for p in points_a] + [p[1] for p in points_b]
        max_val = max([max(xs),max(ys)])
        colors = [self.color_a] * len(points_a) + \
                 [self.color_b] * len(points_b)
        #colors = [self.color_a] + [self.color_b];
        self.axes.plot(*lines)
        self.axes.scatter(xs,ys,c=colors)
        self.axes.plot([0,max_val],[0,max_val],color="red")

    def KeyEvent(self, event) :
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.a_index = (self.a_index - 1) % len(self.persistence_a)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            self.a_index = (self.a_index + 1) % len(self.persistence_a)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_UP :
            self.b_index = (self.b_index - 1) % len(self.persistence_b)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_DOWN :
            self.b_index = (self.b_index + 1) % len(self.persistence_b)
            self.refresh()
            wx.PostEvent(self,wx.PaintEvent())
        else :
            pass
        event.Skip()

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()


class App(wx.App):
    def __init__(self, arg, persistence_a, persistence_b, degree, 
                 index_a = None, index_b = None):
        self.persistence_a = persistence_a
        self.persistence_b = persistence_b
        self.degree = degree
        self.index_a = index_a
        self.index_b = index_b
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.persistence_a, 
                            self.persistence_b, 
                            self.degree,
                            self.index_a,
                            self.index_b)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser(description="utility to plot \
    the bottleneck distance between two persistence diagrams.")
    parser.add_argument("-a", "--persistence-a")    
    parser.add_argument("-b", "--persistence-b")
    parser.add_argument("-d", "--degree", type=int, default=1)
    parser.add_argument("--index-a", type=int)
    parser.add_argument("--index-b", type=int)
    args = parser.parse_args(argv[1:])
    if args.persistence_a == None or not os.path.isfile(args.persistence_a) :
        print "%s : --persistence-a (%s) must specify file that exists" % \
            (argv[0], args.persistence_a)
        sys.exit(0)
    if args.persistence_b == None :
        args.persistence_b = args.persistence_a
    if not os.path.isfile(args.persistence_b) :
        print "%s : --persistence-b (%s) must specify file that exists" % \
            (argv[0], args.persistence_b)
        sys.exit(0)

    persistence_json = load_data(args.persistence_a, "persistence_diagrams", None, None, argv[0] + " : ")
    if persistence_json == None :
        print "Could not load --persistence-a : %s" % (args.persistence_a,)
        exit()
    persistence_a = PD.fromJSONDict(persistence_json)

    persistence_json = load_data(args.persistence_b, "persistence_diagrams", None, None, argv[0] + " : ")
    if persistence_json == None :
        print "Could not load --persistence-b : %s" % (args.persistence_b,)
        exit()
    persistence_b = PD.fromJSONDict(persistence_json)

    try:
        app = App(0, 
                  persistence_a.diagrams, 
                  persistence_b.diagrams, 
                  args.degree,
                  args.index_a,
                  args.index_b)
        app.MainLoop()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__" :
    main(sys.argv)
