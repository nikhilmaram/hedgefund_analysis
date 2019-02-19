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

def calculate_week(curr_date):
    ## date(yyyy,mm,dd)
    start_date = date(2006, 8, 3)

    start_monday = (start_date - timedelta(days=start_date.weekday()))
    # curr_date = date(year, month, day)
    curr_monday = (curr_date - timedelta(days=curr_date.weekday()))

    week_num = int((curr_monday - start_monday).days / 7)
    # print("Week Number : {0}".format(week_num))
    return week_num

def calculate_date(start_date,week):
    end_date = start_date + timedelta(days=week*7)
    return end_date


def parse_trader_book():
    file_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/Trader_Book_Account.xlsx"
    # file_path = "./Trader_Book_Account.xlsx"
    df = pd.read_excel(file_path)
    traders_list = df["name"].tolist()
    account_list = df["Account"].tolist()
    account_to_trader_dict = {}
    trader_to_account_dict = {}
    for trader, account_string in zip(traders_list,account_list):
        # print(trader,account_string)
        trader = trader.lower().replace(".","_")
        for account in account_string.split(","):
            account = account.strip()
            account_to_trader_dict[account] = account_to_trader_dict.get(account,[])
            account_to_trader_dict[account].append(trader)
        trader_to_account_dict[trader] = account_string.split(",")
            # print(account)

    # print(account_to_trader_dict)
    # print(trader_to_account_dict)
    # for account, account_trader_list in account_to_trader_dict.items():
    #     if(len(account_trader_list) > 1):
    #         print(account, account_trader_list)
    print(trader_to_account_dict)
    return account_to_trader_dict,trader_to_account_dict



if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    # create_stock_file('./performance_data/Trader_Book_Account.xlsx')
    # print(calculate_week(date(2013,2,2)))
    # start_date = date(2006, 7, 31)
    # print(calculate_date(start_date,2))
    parse_trader_book()