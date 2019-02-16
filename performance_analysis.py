"""Different performance analysis from the book data"""
import pandas as pd
from datetime import  datetime,timedelta,date

def remove_outliers(dates,performance):
    idx_list = [x[0] for x in enumerate(performance) if abs(x[1]) > 2]
    for idx in sorted(idx_list, reverse=True):
        del performance[idx]
        del dates[idx]
    return dates,performance

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

def performance_given_book(df):
    """Data frame contains the information about the book"""
    df["date"] = df["date"].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    df = df.sort_values("date")
    df = df[["date", "delta", "PnL_MTD_adjusted", "AccountingFile_PnL_MTD", "year_month"]]
    dates, performance = generate_delta_values(df)
    dates, performance = remove_outliers(dates, performance)
    return dates,performance



def performance(book_list):
    """Will return the performance given book list."""
    file = "data/performance_data/PnL_final.csv"
    df = pd.read_csv(file)
