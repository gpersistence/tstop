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
import csv
import argparse
import time
import multiprocessing

from persistence.py_persistence import ZeroDimensionPersistence

# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib
matplotlib.use('wx')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import wx
import numpy

def parse_data(filename, data_index) :
    with open(filename, 'r') as data_file :
        for line in data_file :
            if line.startswith('@DATA') :
                break
        data_reader = csv.reader(data_file, delimiter=',')
        full_data = [line for line in data_reader]

    return [float(d[data_index]) for d in full_data]

def update_points(prev, this, data, index) :
    updated = []
    for p in this :
        old = sorted([u for u in prev if u[0] == p[0] and u[1] == p[1]], key=(lambda x: x[2]))
        found = len([u for u in updated if u[0] == p[0] and u[1] == p[1]])
        if (found >= len(old)) :
            updated.append((p[0],p[1],0))
        else :
            updated.append((p[0],p[1],old[found][2]+1))
    lines = []
    old_zeroes = [p for p in prev if p[2] == 0] if prev != None else []
    new_zeroes = [p for p in updated if p[2] == 0]
    print old_zeroes, new_zeroes
    for n in new_zeroes :
        match = [o for o in old_zeroes if o[1] == n[1]]
        if match != [] :
            lines.append(([n[0],n[1]], [n[1], n[1]]))
    ix = index - 1
    if ix > 0 :
        last = data[ix]
        ix = ix - 1
        while ix >= 0:
            if last > data[ix] :
                last = data[ix]
                ix = ix - 1
            else :
                break
        if ix < index - 2 :
            # monotonically increasing segment...
            lines.append(([last,last], [last,data[index-1]]))
        
    return updated, lines

def compute_thread(data, points) :
    data_len = len(data)
    zdp = ZeroDimensionPersistence()
    last = None
    for (d,i) in zip(data, range(data_len)) :
        zdp.add_function_value(i, float(i), d)
        result = zdp.sweep_persistence()
        (last,lines) = update_points(last, result, data, i)
        points.append((last,lines))

class CanvasFrame(wx.Frame):

    def __init__(self, args, data_1, data_2, points_1, points_2):
        wx.Frame.__init__(self,None,-1,
                          'Comparison of Zero Dimensional Persistence Diagrams',size=(1024,768))

        self.args = args
        self.data_1 = data_1
        self.data_2 = data_2
        self.points_1 = points_1
        self.points_2 = points_2
    

        # Set bot and top to the number of outliers you want to clip from your data
        hist = numpy.histogram(self.data_1, bins=50)
        size = len(self.data_1)
        bot = 0 # size / 100
        for i in range(len(hist[0])) :
            self.min_sig_1 = hist[1][i]
            if bot - hist[0][i] < 0: 
                break
            else :
                bot = bot - hist[0][i]
        top = 0 # size / 100
        for i in range(len(hist[0]), 0, -1) :
            self.max_sig_1 = hist[1][i]
            if top - hist[0][i-1] < 0: 
                break
            else :
                top = top - hist[0][i-1]
    
    
        self.min_sig_2 = min(self.data_2)
        self.max_sig_2 = max(self.data_2)
        hist = numpy.histogram(self.data_2, bins=50)
        size = len(self.data_2)
        bot = 0 # size / 100
        for i in range(len(hist[0])) :
            self.min_sig_2 = hist[1][i]
            if bot - hist[0][i] < 0: 
                break
            else :
                bot = bot - hist[0][i]
        top = 0 # size / 100
        for i in range(len(hist[0]), 0, -1) :
            self.max_sig_2 = hist[1][i]
            if top - hist[0][i-1] < 0: 
                break
            else :
                top = top - hist[0][i-1]
    
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.persistence_axes_1 = self.figure.add_subplot(221)
        self.persistence_axes_2 = self.figure.add_subplot(222)
        self.signal_axes_1      = self.figure.add_subplot(223)
        self.signal_axes_2      = self.figure.add_subplot(224)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.title = self.figure.suptitle("Zero Dimensional Persistence")
        self.background = self.persistence_axes_1.figure.canvas.copy_from_bbox(self.persistence_axes_1.bbox)
        self.colors = ['black', 'red', 'yellow', 'orange', 'blue', 'green', 'violet']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
    
        self.step = 1
        self.frame_1 = 0
        self.frame_2 = 0
        self.cmap = plt.cm.get_cmap('hot')
    
    
        self.point_Refresh()

    def point_Refresh(self) :
        self.canvas.restore_region(self.background)
        self.persistence_axes_1.cla()
        self.persistence_axes_1.set_title("Zero Persistence at step %s" % self.frame_1)
        if self.frame_1 < len(self.points_1) :
            xs  = [p[0] for p in self.points_1[self.frame_1][0]]
            ys  = [p[1] for p in self.points_1[self.frame_1][0]]
            age = [p[2] for p in self.points_1[self.frame_1][0]]
            
            min_val = min(xs+ys) if xs != [] else 0.0
            max_val = max(xs+ys) if xs != [] else 1.0
            if age != [] :
                self.persistence_axes_1.scatter(xs, ys, marker='+', c=age, vmin=min(age), vmax=max(age), cmap=self.cmap)
            self.persistence_axes_1.plot([self.min_sig_1, self.max_sig_1], [self.min_sig_1, self.max_sig_1], color='r')
            for l in self.points_1[self.frame_1][1] :
                self.persistence_axes_1.plot(l[0],l[1], color='#dd2222')
                    
            self.persistence_axes_1.set_xlim([self.min_sig_1, self.max_sig_1])
            self.persistence_axes_1.set_ylim([self.min_sig_1, self.max_sig_1])

        self.persistence_axes_2.cla()
        self.persistence_axes_2.set_title("Zero Persistence at step %s" % self.frame_2)
        if self.frame_2 < len(self.points_2) :
            xs  = [p[0] for p in self.points_2[self.frame_2][0] if p[2] != -1]
            ys  = [p[1] for p in self.points_2[self.frame_2][0] if p[2] != -1]
            age = [p[2] for p in self.points_2[self.frame_2][0] if p[2] != -1]

            min_val = min(xs+ys) if xs != [] else 0.0
            max_val = max(xs+ys) if xs != [] else 1.0
            if age != [] :
                self.persistence_axes_2.scatter(xs, ys, marker='+', c=age, vmin=min(age), vmax=max(age), cmap=self.cmap)
            self.persistence_axes_2.plot([self.min_sig_2, self.max_sig_2], [self.min_sig_2, self.max_sig_2], color='r')
            for l in self.points_2[self.frame_2][1] :
                self.persistence_axes_2.plot(l[0],l[1], color='#dd2222')
            self.persistence_axes_2.set_xlim([self.min_sig_2, self.max_sig_2])
            self.persistence_axes_2.set_ylim([self.min_sig_2, self.max_sig_2])
        
        self.signal_axes_1.cla()
        self.signal_axes_1.set_title("%s data index %s" % (self.args.input_1, self.args.data_index_1))
        self.signal_axes_1.plot(range(self.frame_1), self.data_1[0:self.frame_1], color='r')
        self.signal_axes_1.plot(range(self.frame_1, len(self.data_1)), self.data_1[self.frame_1:], color='g')    
        self.signal_axes_1.set_ylim([self.min_sig_1, self.max_sig_1])
        self.signal_axes_2.cla()
        self.signal_axes_2.set_title("%s data index %s" % (self.args.input_2, self.args.data_index_2))
        self.signal_axes_2.plot(range(self.frame_2), self.data_2[0:self.frame_2], color='r')
        self.signal_axes_2.plot(range(self.frame_2, len(self.data_2)), self.data_2[self.frame_2:], color='g')    
        self.signal_axes_2.set_ylim([self.min_sig_2, self.max_sig_2])
        

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        print "Key code %s" % keycode
        if keycode == wx.WXK_LEFT or keycode == wx.WXK_DOWN :
            self.step = (self.step - 1) if self.step > 1 else self.step
            print self.step
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT or keycode == wx.WXK_UP :
            self.step = (self.step + 1)
            print self.step
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == 65 : # 'A'
            self.frame_1 = (self.frame_1 - self.step) if self.frame_1 > self.step else 0
            print self.frame_1
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == 68 : # 'D'
            self.frame_1 = (self.frame_1 + self.step) if (self.frame_1 + self.step) < len(self.data_1) else (len(self.data_1) - 1)
            print self.frame_1
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == 74 : # 'J'
            self.frame_2 = (self.frame_2 - self.step) if self.frame_2 > self.step else 0
            print self.frame_2
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == 76 : # 'L'
            self.frame_2 = (self.frame_2 + self.step) if (self.frame_2 + self.step) < len(self.data_2) else (len(self.data_2) - 1)
            print self.frame_2
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        else :
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
            event.Skip()
            
    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()

class App(wx.App):
    def __init__(self, arg, args, data_1, data_2, points_1, points_2):
        self.argv = (args, data_1, data_2, points_1, points_2)
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.argv[0], self.argv[1], self.argv[2], self.argv[3], self.argv[4])
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(args, data_1, data_2, points_1, points_2) :
    app = App(0, args, data_1, data_2, points_1, points_2)
    app.MainLoop()

def main(argv) :
    current_dir = os.getcwd()

    processes = []
    try:
        parser = argparse.ArgumentParser(description="Plots zero dimensional persistence diagrams from time series data")
        parser.add_argument("--input-1", "-i")
        parser.add_argument("--input-2", "-j")
        parser.add_argument("--data-index-1", "-d", type=int, default=0)
        parser.add_argument("--data-index-2", "-e", type=int, default=0)

        args = parser.parse_args(argv[1:])

        data_1 = parse_data(args.input_1, args.data_index_1)
        if args.input_2 != None :
            data_2 = parse_data(args.input_2, args.data_index_2)
        else :
            data_2 = data_1

        manager = multiprocessing.Manager()
        points_1 = manager.list([])
        points_2 = manager.list([])
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=(args, data_1, data_2, points_1, points_2,))
        points_1_thread = \
          multiprocessing.Process(target=compute_thread,
                                  args=(data_1, points_1,))
        points_2_thread = \
          multiprocessing.Process(target=compute_thread,
                                  args=(data_2, points_2,))
        display_thread.start()
        processes.append(display_thread)
        points_1_thread.start()
        processes.append(points_1_thread)
        points_2_thread.start()
        processes.append(points_2_thread)
        display_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        
    for p in processes :
        if p.is_alive():
            p.terminate()
    exit(0)
        

if __name__ == "__main__":
    main(sys.argv)
