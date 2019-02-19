"""Different performance analysis from the book data"""
import pandas as pd
from datetime import  datetime,timedelta,date
import misc
import pickle

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



def performance(book_list,week):
    """Will return the performance given book list in the given week. Because, the book list  is different in every week."""
    file = "data/performance_data/PnL_final.csv"
    ### Each value in the performance list is performance of the book in that week.
    performance_list = []
    df = pd.read_csv(file)
    # df["date"] = df["date"].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    ## Week w.r.t each entry
    df["date"] = df["date"].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    df["week"] = df["date"].apply(lambda x : misc.calculate_week(x.date()))
    df = df.sort_values("date")
    for book in book_list:
        ## get the dataframe corresponding to this book.
        df_book = df[df["book"]==book]
        ## calculate the cumulative for each month for this book.
        df_book["cumulative"] = 0
        ## need to adjust for month ending
        cumulative_sum = 0
        # print(df_book)
        for month, df_month_group in df_book.groupby("year_month"):
            # print(month)
            df_book["cumulative"][df_book["year_month"] == month] = cumulative_sum + \
                                                                    df_book["PnL_MTD_adjusted"][
                                                                        df_book["year_month"] == month]
            cumulative_sum = df_book[df_book["year_month"] == month].iloc[-1]["cumulative"]
        # print(df_book)
        ## Get the cumulative book data corresponding to the week.
        df_book_week = df_book[df_book["week"] == week]
        book_weeek_performance_list = df_book_week["cumulative"].tolist()
        if(len(book_weeek_performance_list) > 1):
            performance_value = (book_weeek_performance_list[-1] - book_weeek_performance_list[0])/book_weeek_performance_list[0]
        else:
            performance_value = 0
        performance_list.append(performance_value)

    # print(performance_list)
    ## Combined performance is the sum of all performances.
    return sum(performance_list)


def precompute_performance_all_weeks():
    """Compute the performance of each book w.r.t week and store them"""
    books_list = pd.read_csv("data/performance_data/stock.csv",index_col=False).iloc[:,0].tolist()
    file = "data/performance_data/PnL_final.csv"
    df = pd.read_csv(file)
    df = df.fillna(0)
    # df["date"] = df["date"].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    ## Week w.r.t each entry
    df["date"] = df["date"].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    df["week"] = df["date"].apply(lambda x: misc.calculate_week(x.date()))
    df = df.sort_values("date")
    output_df = pd.DataFrame(columns=["book","week","performance"])
    output_dict = {}
    print(books_list)
    for book in books_list:
        df_book = df[df["book"] == book]
        ## calculate the cumulative for each book.
        df_book["cumulative"] = 0
        ## need to adjust for month ending
        cumulative_sum = 0
        # print(df_book)
        for month, df_month_group in df_book.groupby("year_month"):
            # print(month)
            df_book["cumulative"][df_book["year_month"] == month] = cumulative_sum + \
                                                                    df_book["PnL_MTD_adjusted"][
                                                                        df_book["year_month"] == month]
            cumulative_sum = df_book[df_book["year_month"] == month].iloc[-1]["cumulative"]
        output_dict[book] = output_dict.get(book,{})
        for week in range(0,341):
            df_book_week = df_book[df_book["week"] == week]
            # print(book,week)
            # print(df_book_week)
            book_weeek_performance_list = df_book_week["cumulative"].tolist()
            performance_value = 0
            if (len(book_weeek_performance_list) > 1):
                performance_value = (book_weeek_performance_list[-1] - book_weeek_performance_list[0]) /(book_weeek_performance_list[0] +1)
            else:
                performance_value = 0
            # output_df = output_df.append({"book":book,"week":week,"performance":performance_value},ignore_index=True)
            # print(book,week,performance_value)
            output_dict[book][week] = performance_value
    with open(
            "./data/performance_data/PnL_weekly_aggregated.pkl",
            "wb") as handle:
        pickle.dump(output_dict, handle)

    output_df.to_csv("./data/performance_data/PnL_weekly_aggregated.csv")
    # print(output_df)


if __name__ == "__main__":
    pd.options.mode.chained_assignment = None
    pd.set_option('display.max_colwidth', -1)
    # print(performance(['CROS', ' MSVC', 'TFSH', 'MEN2', 'MIEI', ' MIER', 'GLS1', ' GLS2', ' GLS3'],125))
    precompute_performance_all_weeks()