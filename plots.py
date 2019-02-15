import matplotlib.pyplot as plt
import os
import csv
import numpy as np
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter,DayLocator
from datetime import  datetime,timedelta,date
from matplotlib.dates import MONDAY
import pandas as pd

import collections
from collections import Counter

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

    # ## Remove the outlier
    # idx_list = [x[0] for x in enumerate(y_list[0]) if abs(x[1]) == 0]
    # for idx in sorted(idx_list, reverse=True):
    #     del dates[idx]
    #     for core_number in range(1,10):
    #         print(idx,core_number)
    #         del y_list[core_number-1][idx]



    ratio = False
    if(ratio):
        for i in range(1,len(y_list)):
            # plt.plot(x, y_list[i],'-o', label='%d-core' % (i+1))
            ax.plot_date(dates, np.divide(y_list[i],y_list[0]), '-o', label='%d-core' % (i + 1))
    else:
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
    # plt.grid()
    plt.show()


def plot_edge_distribution(edge_directory):
    ### plots the edge distribution
    file_names_list = []
    for (dirpath, dirnames, filenames) in os.walk(edge_directory):
        for filename in filenames:
            if filename.startswith("edge_distribution"):
                file_names_list.append(os.path.join(edge_directory, filename))

    plot_dict = {}
    for file_name in file_names_list:
        with open(file_name) as csv_file:
            reader = csv.reader(csv_file)
            mydict = dict((int(float(x[0])), int(x[1])) for x in reader)
            # print(mydict)
            plot_dict = Counter(plot_dict) + Counter(mydict)
            # print(plot_dict)

    plot_dict.pop(0,None)
    plot_dict = collections.OrderedDict(sorted(plot_dict.items()))
    keys_list = list(plot_dict.keys())
    values_list = list(plot_dict.values())

    print(keys_list,values_list)

    end_number = 50
    plt.plot(keys_list[:end_number],values_list[:end_number])
    plt.show()

def generate_delta_values(df_grouped):
    # print(df_grouped)
    df_grouped = df_grouped.fillna(0)
    dates = df_grouped["date"].tolist()

    # delta = df_grouped["delta"].tolist()
    performance = df_grouped["PnL_MTD_adjusted"].tolist()
    # delta = [float(accounting[i + 1]) - float(accounting[i]) for i in range(len(accounting) - 1)]
    # delta.insert(0, 0)
    ## since MTD is given, for a new month it would be difference between end of the last month.

    df_grouped["cumulative"] = 0
    ## need to adjust for month ending
    cumulative_sum = 0
    for month, df_month_group in df_grouped.groupby("year_month"):
        # print(month)
        df_grouped["cumulative"][df_grouped["year_month"]==month] = cumulative_sum + df_grouped["PnL_MTD_adjusted"][df_grouped["year_month"]==month]
        cumulative_sum = df_grouped[df_grouped["year_month"]==month].iloc[-1]["cumulative"]
        # print(cumulative_sum)

    ## if cumulative sum is needed for performance
    performance = df_grouped["cumulative"].tolist()
    ## if difference is needed for performance.
    performance = [(float(performance[i + 1]) - float(performance[i]))/(float(performance[i]) +1) for i in range(len(performance) - 1)]
    performance.insert(0, 0)
    return dates,performance

def plot_book(file,book_name):
    df = pd.read_csv(file)
    # print(df)
    fig, ax = plt.subplots()
    for book,df_grouped in df.groupby("book"):
        if book == book_name:
            # print(df_grouped)
            ## Replacing nan with 0
            df_grouped["date"] = df_grouped["date"].apply(lambda x : datetime.strptime(x,'%m/%d/%Y'))
            df_grouped = df_grouped.sort_values("date")
            df_grouped =df_grouped[["date","delta","PnL_MTD_adjusted","AccountingFile_PnL_MTD","year_month"]]
            dates,performance = generate_delta_values(df_grouped)
            dates,performance = remove_outliers(dates,performance)
            start_number = 0
            end_number = -1
            print(dates[start_number:end_number])
            print(performance[start_number:end_number])
            ax.plot_date(dates[start_number:end_number], performance[start_number:end_number] , '-o', label=book)

    months = MonthLocator(range(1, 13), bymonthday=3, interval=1)
    days = DayLocator(bymonthday=range(1, 30), interval=1)
    monthsFmt = DateFormatter("%b '%y")
    mondays = WeekdayLocator(MONDAY)

    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mondays)
    # ax.xaxis.set_minor_locator(days)
    ax.autoscale_view()
    # plt.plot_date(date[:10],delta[:10])
    plt.xlabel("Time")
    plt.ylabel("Book PnL")
    plt.title("Book PnL vs Time")
    plt.legend()
    plt.show()


def remove_outliers(dates,performance):
    idx_list = [x[0] for x in enumerate(performance) if abs(x[1]) > 2]
    for idx in sorted(idx_list, reverse=True):
        del performance[idx]
        del dates[idx]
    return dates,performance

def plot_user_sentiment(file,title,label):
    df = pd.read_csv(file,names=["date","sentiment"])
    df["date"] = df["date"].apply(lambda x: datetime.strptime(str(x), '%m-%d-%Y'))
    df = df.sort_values("date")

    dates = df["date"].tolist()
    sentiment = df["sentiment"].tolist()

    print(dates)
    fig, ax = plt.subplots()
    start_number = 540
    end_number = 585
    print(sentiment[start_number:end_number])
    ax.plot_date(dates[start_number:end_number], sentiment[start_number:end_number], '-o', label=label)
    days = DayLocator(bymonthday=range(1,30),interval=1)
    months = MonthLocator(range(1, 13), bymonthday=1, interval=1)
    monthsFmt = DateFormatter("%b %y")
    mondays = WeekdayLocator(MONDAY)

    ax.xaxis.set_major_locator(months)
    # ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(monthsFmt)
    # ax.xaxis.set_minor_locator(mondays)
    ax.xaxis.set_minor_locator(days)
    ax.autoscale_view()

    plt.xlabel("Time")
    plt.ylabel("Sentiment")
    plt.title(title)
    plt.legend()
    plt.show()
    # print(df)
    # print(df["date"].tolist())
    # print(df["sentiment"].tolist())
    # pass



if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    # pd.set_option("display.max_rows", -1)

    complete_ims_kcore_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/kcore_weighted/threshold_100/"
    business_ims_kcore_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/kcore_business_weighted/threshold_100/"
    personal_ims_kcore_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/kcore_personal_weighted/threshold_100/"

    ### Largest Connected Component

    # plot_element_kcore(complete_ims_kcore_path, 120, 150, "kcore_largest_cc_num_nodes", "Time",
    #                    "Number of Nodes in Largest Connected Component",
    #                    "Number of Nodes in Largest Connected Component Vs Time")

    # plot_element_kcore(business_ims_kcore_path, 120, 150, "kcore_largest_cc_num_nodes", "Time",
    #                    "Number of Nodes in Largest Connected Component",
    #                    "Threshold 100 : Number of Nodes in Largest Connected Component Vs Time : Business")
    # # #
    # plot_element_kcore(personal_ims_kcore_path, 120, 150, "kcore_largest_cc_num_nodes", "Time",
    #                    "Number of Nodes in Largest Connected Component",
    #                    "Threshold 100 : Number of Nodes in Largest Connected Component Vs Time : Personal")

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
    # plot_edge_distribution("/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/edge_distribution/")

    plot_book(
        "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/PnL_final.csv",
        "ALTM")

    # plot_user_sentiment(
    #     "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/user_sentiment_personal/wolfbergADAM.csv",
    #     "Sentiment vs Time : Personal: Received Messages","ADAM")

    # plot_user_sentiment(
    #     "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/user_sentiment_business/feinsteinandrea.csv",
    #     "Sentiment vs Time : Business : Sent Messages","AFEI")

    # plot_user_sentiment(
    #     "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/user_sentiment_personal/sapanskilawrence_sedoymichael_received.csv",
    #     "Sentiment vs Time : Personal: Received Messages","MENG")