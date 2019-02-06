import nltk as nk
import pandas as pd
import csv
from datetime import  datetime,timedelta,date
def create_stock_file(file):
    """Creates a stock file from reading Trader Book Account xlsx"""
    df = pd.read_excel(file)
    stock_list = []

    for i in range(len(df)):
        for stock in df['Account'][i].split(','):
            if not stock.strip() == "":
                stock_list.append(stock.strip())

    stock_list = sorted(set(stock_list))
    stockfile = open("./performance_data/stock.csv", 'w')
    for stock in stock_list:
        stockfile.write(stock+"\n")
    stockfile.close()

def calculate_week(year,month,day):
    ## date(yyyy,mm,dd)
    start_date = date(2006, 8, 3)

    start_monday = (start_date - timedelta(days=start_date.weekday()))
    curr_date = date(year, month, day)
    curr_monday = (curr_date - timedelta(days=curr_date.weekday()))

    week_num = int((curr_monday - start_monday).days / 7)
    print("Week Number : {0}".format(week_num))

def calculate_date(start_date,week):
    end_date = start_date + timedelta(days=week*7)
    return end_date

if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    # create_stock_file('./performance_data/Trader_Book_Account.xlsx')
    calculate_week(2008,12,12)
    # start_date = date(2006, 7, 31)
    # print(calculate_date(start_date,2))