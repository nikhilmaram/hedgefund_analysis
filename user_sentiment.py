## Finding the user and calculating his sentiment in a week.
import os
import multiprocessing
import pandas as pd
from datetime import  datetime,timedelta,date
import csv


def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))

def user_sentiment(dir_path,filenames,output_path,user_last_name,user_first_name,output_dict):
    """Generates the user sentiment file given the username"""

    process_count = multiprocessing.current_process().name
    output_list = []

    ## This should be generated based on reading from Address_linkfile.txt
    # buddy_names = ["awolf11","awolfberg"]
    buddy_names = buddy_names_given_user(user_last_name,user_first_name)
    print(buddy_names)

    for filename in filenames:
        file_path = os.path.join(dir_path, filename)
        print(file_path)
        df = pd.read_csv(file_path)
        df = df[['sender_buddy','receiver_buddy','content','time_stamp','sentiment']]

        ## Get only those rows who have sender as in given buddy
        df = df[df.sender_buddy.isin(buddy_names)]
        # df = df[df.receiver_buddy.isin(buddy_names)]
        df["day"] = df["time_stamp"].apply(lambda x : datetime.strptime(x,'%m-%d-%yT%H:%M:%S').strftime("%m-%d-%Y"))

        ## Group it by day to calculate the sentiment for each day
        for day, df_grouped in df.groupby("day"):
            # print(day)
            # print(df_grouped)
            sentiment_list = df_grouped["sentiment"].tolist()
            # sentiment = 1 if (sentiment_list.count(1) >= sentiment_list.count(-1)) else -1
            positive_sentiment_count = sentiment_list.count(1)
            negative_sentiment_count = sentiment_list.count(-1)

            # sentiment = sum(sentiment_list)/len(sentiment_list)
            sentiment = sum(sentiment_list)/(positive_sentiment_count + negative_sentiment_count+1)
            # print(sentiment_list.count(0),sentiment_list.count(1),sentiment_list.count(-1))
            # print(sentiment,sentiment_list)csv_writer.writerow([day, sentiment])
            output_list.append([day, sentiment])

        # print(df)
    output_dict[process_count] = output_list

def sentiment_between_two_users(dir_path,filenames,output_path,
                                user1_last_name,user1_first_name,user2_last_name,user2_first_name,output_dict):
    """Generates the user sentiment file given the username"""
    process_count = multiprocessing.current_process().name
    output_list = []


    ## This should be generated based on reading from Address_linkfile.txt
    # buddy_names = ["awolf11","awolfberg"]
    buddy_names = buddy_names_given_user(user1_last_name,user1_first_name)
    print(buddy_names)
    buddy_names.extend(buddy_names_given_user(user2_last_name,user2_first_name))
    print(buddy_names)

    for filename in filenames:
        file_path = os.path.join(dir_path, filename)
        print(file_path)
        df = pd.read_csv(file_path)
        df = df[['sender_buddy','receiver_buddy','content','time_stamp','sentiment']]

        ## Get only those rows who have sender as in given buddy
        # df = df[df.sender_buddy.isin(buddy_names)]
        df = df[df.receiver_buddy.isin(buddy_names)]
        df["day"] = df["time_stamp"].apply(lambda x : datetime.strptime(x,'%m-%d-%yT%H:%M:%S').strftime("%m-%d-%Y"))

        ## Group it by day to calculate the sentiment for each day
        for day, df_grouped in df.groupby("day"):
            # print(day)
            # print(len(df_grouped))
            sentiment_list = df_grouped["sentiment"].tolist()
            # sentiment = 1 if (sentiment_list.count(1) >= sentiment_list.count(-1)) else -1
            positive_sentiment_count = sentiment_list.count(1)
            negative_sentiment_count = sentiment_list.count(-1)

            # sentiment = sum(sentiment_list)/len(sentiment_list)
            sentiment = sum(sentiment_list)/(positive_sentiment_count + negative_sentiment_count+1)
            # print(sentiment_list.count(0),sentiment_list.count(1),sentiment_list.count(-1))
            # print(sentiment,sentiment_list)
            # print(day,sentiment)
            output_list.append([day,sentiment])

    ## append the output list to dictionary
    output_dict[process_count] = output_list

def buddy_names_given_user(user_last_name,user_first_name):
    address_file_name = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/Address_linkfile.txt"

    f = open(address_file_name,"r")
    user_address_list = []
    for line in f.readlines():
        line_split = line.split()
        last_name = line_split[0]
        address = line_split[-1]
        first_name = line_split[-2]
        # print(last_name,first_name,address)
        if(first_name.lower() == user_first_name.lower() and last_name.lower() == user_last_name.lower()):
            user_address_list.append(address)
    return user_address_list


if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)

    # dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/sentiment_personal/"

    # dir_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/sentiment_business/"
    # output_path = "./data/user_sentiment_business/"

    dir_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/sentiment_personal/"
    output_path = "./data/user_sentiment_personal/"

    file_names_list = []
    for (dirpath, dirnames, filenames) in os.walk(dir_path):
        for filename in filenames:
            file_names_list.append(filename)

    # file_names_list = file_names_list[:10]
    num_process = 16
    # print(file_names_list)
    chunked_file_names_list = list(chunker_list(file_names_list, num_process))
    print(chunked_file_names_list)


    manager = multiprocessing.Manager()
    output_dict = manager.dict()
    count = 0

    user1_last_name = "sapanski" ; user1_first_name = "lawrence" ; user2_last_name = "sedoy" ;user2_first_name = "michael"
    output_file_name = user1_last_name + user1_first_name + "_" + user2_last_name + user2_first_name + ".csv"
    # output_file_name = user_last_name + user_first_name + ".csv"
    # user_last_name = "feinstein" ; user_first_name = "andrea"

    process_list =[]
    for file_names in chunked_file_names_list:
        # p = multiprocessing.Process(target=user_sentiment,
        #                             args=(dir_path, file_names, output_path,user_last_name , user_first_name,output_dict),
        #                                                             name=count)
        p = multiprocessing.Process(target=sentiment_between_two_users,
                                    args=(dir_path, file_names, output_path, user1_last_name,user1_first_name,user2_last_name,user2_first_name,output_dict,),
                                    name=count)
        process_list.append(p)
        p.start()
        count = count + 1

    for process in process_list:
        process.join()

    # print(output_dict)




    myfile = open(output_path + output_file_name, "w")
    csv_writer = csv.writer(myfile)

    ## Write the user sentiment into files
    for process,process_output_list in output_dict.items():
        for date_sentiment_list in process_output_list:
            # print(date_sentiment_list)
            csv_writer.writerow(date_sentiment_list)

    # print(buddy_names_given_user("sedoy","michael"))