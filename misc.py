import nltk as nk
import pandas as pd
import csv
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




if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    create_stock_file('./performance_data/Trader_Book_Account.xlsx')
