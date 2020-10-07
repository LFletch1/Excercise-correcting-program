#!/usr/bin/env python3
# Lance Fletcher
# July 26, 2020

import matplotlib.pyplot as plt
import scipy.signal


class Curve:
    def __init__(self, start=0, end=0):
        self.start = start
        self.end = end


class Plot:
    def __init__(self, values):
        self.values = values
        self.curves = []
        self.low = 2000  # start with high value to make first number the low
        self.high = -2000  # start with low value to make the first number the high
        self.start = 0
        self.end = 0
        self.high_index = 0
        self.low_index = 0
        self.rising = False
        self.falling = True

    def create_curve(self, start, end):
        new_curve = Curve(start, end)
        self.curves.append(new_curve)


def graph_graded_smooth_plot(array_of_points, array_of_grades):
    sg_angles = scipy.signal.savgol_filter(array_of_points, 55, 3)
    sg_plot = Plot(sg_angles)
    index = 0
    consecutive_changes = 0
    lows = []
    low_indexes = []
    highs = []
    high_indexes = []
    while index < len(sg_plot.values):
        if sg_plot.falling:  # values are going down in value
            if consecutive_changes == 10:  # Curve has been rising for 10 indexes
                # print('low:', sg_plot.low_index)
                sg_plot.falling = False
                sg_plot.rising = True
                # plt.plot(sg_plot.low_index, sg_plot.low)
                lows.append(sg_plot.low)
                low_indexes.append(sg_plot.low_index)
                sg_plot.low = 2000  # Here is where you need to save this index
                consecutive_changes = 0
            elif sg_plot.values[index] < sg_plot.low:
                sg_plot.low = sg_plot.values[index]
                sg_plot.low_index = index
                consecutive_changes = 0
            else:
                consecutive_changes += 1
        else:  # values are going up in value
            if consecutive_changes == 10:  # Curve has been falling for 10 indexes
                # print('high:', sg_plot.high_index)
                sg_plot.rising = False
                sg_plot.falling = True
                highs.append(sg_plot.high)
                high_indexes.append(sg_plot.high_index)
                sg_plot.high = 0
                consecutive_changes = 0
            elif sg_plot.values[index] > sg_plot.high:
                sg_plot.high = sg_plot.values[index]
                sg_plot.high_index = index
                consecutive_changes = 0
            else:
                consecutive_changes += 1
        index += 1

    i = 0
    total = 0
    fig = plt.figure()
    ax = plt.axes()
    ax.set_facecolor('grey')
    fig.patch.set_facecolor('grey')
    linestyles = ('solid', 'dashed', 'dotted', 'dashdot')
    rep = 1
    while i < len(high_indexes) - 1:
        LINESTYLE = rep % 4
        rep_angles = sg_angles[high_indexes[i]:high_indexes[i+1]]
        rep_grades = array_of_grades[high_indexes[i]:high_indexes[i+1]]
        if len(rep_angles) < 50:
            i += 1
            total = 0
            continue
        for num in rep_grades:
            total += num
        average_grade = total/len(rep_grades)
        if average_grade > 85:
            COLOR = 'green'
        elif average_grade > 70:
            COLOR = 'yellow'
        elif average_grade > 55:
            COLOR = 'orange'
        else:
            COLOR = 'red'
        plt.plot(rep_angles, color=COLOR, label='Rep ' + str(rep), linestyle=linestyles[LINESTYLE])
        plt.legend()
        # plt.plot(array_of_points[high_indexes[i]:high_indexes[i+1]], label='Rep'+str(i+1))
        rep += 1
        i += 1
        total = 0

    # plt.show()
    plt.savefig('rep_graph')
