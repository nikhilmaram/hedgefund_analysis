import matplotlib.pyplot as plt
import os
import csv
import numpy as np
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from datetime import  datetime,timedelta,date
from matplotlib.dates import MONDAY

def calculate_date(start_date,week):
    end_date = start_date + timedelta(days=week*7)
    return end_date


def plot_element_kcore(dir_path,week_start,week_end,element_filename_start,xlabel,ylabel,title):
    """Plots largest connected component(cc)"""
    ## dictionary has week as key and values as a dictionary, whose key is core number and value is largest cc for that core number
    kcore_element_dict = {}
    for (dirpath, dirnames, filenames) in os.walk(dir_path):
        for filename in filenames:
            if filename.startswith(element_filename_start):
                file_path = os.path.join(dir_path, filename)
                week_num = int(filename.split('.')[0].split('_')[-1][4:])
                # print(week_num)
                kcore_element_dict[week_num] = {}
                ## Get the corresponding kcore_number_week file because it has the k value
                ## mapping string to integers
                kcore_num_file = os.path.join(dir_path, "kcore_number_week{0}.csv".format(week_num))
                kcore_num_list = list(map(int, open(kcore_num_file).readline().strip("\n").split(",")[:-1]))


                kcore_element_list = list(map(int, open(file_path).readline().strip("\n").split(",")[:-1]))

                ### {<week_num> : {<core_number>: <largest_cc_num_nodes>} }
                kcore_element_dict[week_num] = dict(zip(kcore_num_list, kcore_element_list))

    x = list(range(week_start, week_end))
    # y = [kcore_largest_cc_num_nodes_dict[key][1] for key in x]
    y_list = []
    for core_number in range(1, 10):
        y = []
        for week in x:
            ## In case the core number is not present in the corresponding week.
            if (week in kcore_element_dict.keys()) and (core_number in kcore_element_dict[week].keys()):
                y.append(kcore_element_dict[week][core_number])
            else:
                # print(week,core_number)
                y.append(0)
        y_list.append(y)

    fig, ax = plt.subplots()

    dates = []
    start_date = date(2006, 8, 3)
    for i in range(week_start, week_end):
        dates.append(calculate_date(start_date, i))

    for i in range(len(y_list)):
        # plt.plot(x, y_list[i],'-o', label='%d-core' % (i+1))
        ax.plot_date(dates, y_list[i], '-o', label='%d-core' % (i + 1))

    months = MonthLocator(range(1, 13), bymonthday=1, interval=1)
    monthsFmt = DateFormatter("%b '%y")
    # every monday
    mondays = WeekdayLocator(MONDAY)

    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mondays)
    ax.autoscale_view()

    # my_xticks = ['John', 'Arnold', 'Mavis', 'Matt']
    # plt.xticks(x, my_xticks)
    # plt.xticks([74,79,84,93])

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.show()


if __name__ == "__main__":

    complete_ims_kcore_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/kcore/"
    business_ims_kcore_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/kcore_business/"
    personal_ims_kcore_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/kcore_personal/"


    ### Largest Connected Component

    # plot_element_kcore(complete_ims_kcore_path, 75, 150, "kcore_largest_cc_num_nodes", "Time",
    #                    "Number of Nodes in Largest Connected Component",
    #                    "Number of Nodes in Largest Connected Component Vs Time")

    # plot_element_kcore(business_ims_kcore_path, 225, 265, "kcore_largest_cc_num_nodes", "Time",
    #                    "Number of Nodes in Largest Connected Component",
    #                    "Number of Nodes in Largest Connected Component Vs Time : Business")

    # plot_element_kcore(personal_ims_kcore_path, 225, 265, "kcore_largest_cc_num_nodes", "Time",
    #                    "Number of Nodes in Largest Connected Component",
    #                    "Number of Nodes in Largest Connected Component Vs Time : Personal")

    # ### kcore number of nodes
    #
    #
    # plot_element_kcore(complete_ims_kcore_path, 0, 75, "kcore_num_of_nodes", "Time", "Number of Nodes in K-core",
    #                    "Number of Nodes in K-Core Vs Time")
    # #
    # plot_element_kcore(business_ims_kcore_path, 0, 75, "kcore_num_of_nodes", "Time", "Number of Nodes in K-core",
    #                    "Number of Nodes in K-Core Vs Time : Business")
    #
    # ### Kcore number of components
    #
    # plot_element_kcore(complete_ims_kcore_path, 0, 75, "kcore_num_components", "Time", "Number of Components in K-core",
    #                    "Number of Components in K-Core Vs Time")
    #
    # plot_element_kcore(business_ims_kcore_path, 0, 75, "kcore_num_components", "Time", "Number of Components in K-core",
    #                    "Number of Components in K-Core Vs Time : Business")
    #