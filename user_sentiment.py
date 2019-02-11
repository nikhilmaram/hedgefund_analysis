## Finding the user and calculating his sentiment in a week.
import os
import multiprocessing
import pandas as pd
from datetime import  datetime,timedelta,date
import csv

def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))

def user_sentiment(dir_path,filenames,output_path):
    output_file_name = multiprocessing.current_process().name
    myfile = open(output_path+output_file_name,"w")
    csv_writer = csv.writer(myfile)
    for filename in filenames:
        file_path = os.path.join(dir_path, filename)
        print(file_path)
        df = pd.read_csv(file_path)
        df = df[['sender_buddy','receiver_buddy','content','time_stamp','sentiment']]
        ## Get the only id name from email.
        df['sender_buddy'] = df['sender_buddy'].apply(lambda x : str(x).split('@')[0])
        df['receiver_buddy'] = df['receiver_buddy'].apply(lambda x: str(x).split('@')[0])
        ## This should be generated based on reading from Address_linkfile.txt
        buddy_names = ["awolf11","awolfberg"]
        ## Get only those rows who have sender as in given buddy
        df = df[df.sender_buddy.isin(buddy_names)]
        df["day"] = df["time_stamp"].apply(lambda x : datetime.strptime(x,'%m-%d-%yT%H:%M:%S').strftime("%m-%d-%Y"))

        ## Group it by day to calculate the sentiment for each day
        for day, df_grouped in df.groupby("day"):
            # print(day)
            # print(df_grouped)
            sentiment_list = df_grouped["sentiment"].tolist()
            # sentiment = 1 if (sentiment_list.count(1) >= sentiment_list.count(-1)) else -1
            sentiment = sum(sentiment_list)/len(sentiment_list)
            # print(sentiment_list.count(0),sentiment_list.count(1),sentiment_list.count(-1))
            # print(sentiment,sentiment_list)
            csv_writer.writerow([day, sentiment])
        # print(df)




if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/sentiment_personal/"
    # dir_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/sentiment_business/"
    file_names_list = []
    for (dirpath, dirnames, filenames) in os.walk(dir_path):
        for filename in filenames:
            file_names_list.append(filename)

    num_process = 1
    print(file_names_list)
    chunked_file_names_list = list(chunker_list(file_names_list, num_process))
    print(chunked_file_names_list)
    # output_path = "./user_sentiment_business/"
    output_path = "./user_sentiment_personal/"


    for file_names in chunked_file_names_list:
        p = multiprocessing.Process(target=user_sentiment, args=(dir_path, file_names, output_path,),
                                    name="adam.csv")
        p.start()
