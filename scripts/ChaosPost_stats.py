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


import sys
import numpy
from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Segments import Segments
data = []
for arg in sys.argv[1:] :
    segments = Segments.fromJSONDict(load_data(arg, "segments", None, None, sys.argv[0] + ": "))
    taus = [int(s.tau) for s in segments.segments]
    window_sizes = [len(s.windows[0]) for s in segments.segments]

    data.append([arg[arg.find('-data-')+6:arg.find('-seg-')], min(taus), max(taus), numpy.mean(taus),min(window_sizes), max(window_sizes), numpy.mean(window_sizes)])

data.sort()
print data
import matplotlib.pyplot as plt
f = plt.figure()
axes_tau = f.add_axes([0.1,0.3,0.35,0.6])
axes_tau.set_title("Time Delay")
plots =[
axes_tau.bar(left=range(len(data)), height=[d[1] for d in data], bottom=0.0, width=0.8, color="#a8ddb5"),
axes_tau.bar(left=range(len(data)), height=[d[2] - d[1] for d in data], bottom=[d[1] for d in data], width=0.8, color="#7bccc4"),
axes_tau.bar(left=range(len(data)), height=[d[3] - d[2] for d in data], bottom=[d[2] for d in data], width=0.8, color="#4eb3d3") ]
plt.legend(plots, ["Minimum", "Average", "Maximum"], ncol=3).draggable()
axes_tau.set_xticks([x + 0.5 for x in range(len(data))])
axes_tau.set_xticklabels([d[0] for d in data], rotation=90)
axes_win = f.add_axes([0.5,0.3,0.35,0.6])
axes_win.set_title("Window Size")
axes_win.bar(left=range(len(data)), height=[d[4] for d in data], bottom=0.0, width=0.8, color="#a8ddb5")
axes_win.bar(left=range(len(data)), height=[d[5] - d[4] for d in data], bottom=[d[4] for d in data], width=0.8, color="#7bccc4")
axes_win.bar(left=range(len(data)), height=[d[6] - d[5] for d in data], bottom=[d[5] for d in data], width=0.8, color="#4eb3d3")
axes_win.set_xticks([x + 0.5 for x in range(len(data))])
axes_win.set_xticklabels([d[0] for d in data], rotation=90)

plt.show()
