import config as cfg
import eml_parser
import json
import os
import re
from os import walk
import pandas as pd
import xml.etree.ElementTree as ET
import multiprocessing

import time

from datetime import  datetime,timedelta,date

import itertools

f = open(cfg.STOCK_FILE, 'r')
stock_list = []
for line in f.readlines():
    stock_list.append(line.strip('\n').lower())

stock_set = set(stock_list)

f = open(cfg.TRADING_TERMS,'r')
trading_terms_list = []


for line in f.readlines():
    trading_terms_list.append(line.strip('\n'))

trading_terms_set = set(trading_terms_list)
# print(stock_list)
# print(trading_terms_list)


def split_dict(x, chunks):
    i = itertools.cycle(range(chunks))
    split = [dict() for _ in range(chunks)]
    for k, v in x.items():
        split[next(i)][k] = v
    return split

def classify_ims(text):
    # Checks for number
    if bool(re.match('.*\d+.*', text)):
        return 1
    word_list = text.lower().split(' ')

    # Check for stock list and trading terms
    for word in word_list:
        # if word in stock_list or word in trading_terms_list:
        if word in stock_set or word in trading_terms_set:
            return 1

    return 0

def json_serial(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial

def read_EML_file(eml_file):
    with open(eml_file, 'rb') as fhdl:
        raw_email = fhdl.read()
        parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email, include_raw_body=True)
        # temp_file = open('temp.json', 'w')
        # json.dump(parsed_eml, temp_file, ensure_ascii=False, default=json_serial)
        return parsed_eml

def parse_eml_data(data):
    ## first item in the 'body' value will be actual email.
    try:
        content = data["body"][0]["content"]
    except:
        content = "No Content"

    ## currently taking only one element
    try:
        subject = data["header"]["header"]["subject"][0]
    except:
        subject = "No Subject"

    if "x-sender" in data["header"]["header"].keys():
        sender = data["header"]["header"]["x-sender"][0]
    else:
        sender = data["header"]["header"]["from"][0]
    if "x-receiver" in data["header"]["header"].keys():
        receiver = data["header"]["header"]["x-receiver"][0]
    elif "to" in data["header"]["header"].keys():
        receiver = data["header"]["header"]["to"][0]
    else:
        receiver = "No Receiver"
    time_stamp = data["header"]["header"]["date"][0]

    return sender,receiver,time_stamp,subject,content

# def parse_IM_data(data,im_df,sender,receiver):
def parse_IM_data(data, sender, receiver):
    # # Write into a temporary file to check intermediata XML data
    # file_write = open('temp.xml','w')
    # file_write.write(data)
    # file_write.close()
    im_df = pd.DataFrame(
        columns=['sender', 'sender_buddy', 'receiver', 'receiver_buddy', 'time_stamp', 'subject', 'content',
                 'classify'])
    pattern = "(\<interaction\>)(.*)(\<\/interaction\>)"
    m = re.search(pattern, data, re.DOTALL)

    ## Add the XML header so XML parser can work
    data = cfg.XML_HEADER + m.group(0)

    ## parse the XML data
    root = ET.fromstring(data)
    # print(root.tag)

    sender_buddy = root.find('buddyName').text
    partEntered = root.find('transcript').find('event').find('partEntered')
    receiver_buddy = partEntered.find('buddyName').text

    buddy_to_user = {}
    buddy_to_user[sender_buddy] = sender
    buddy_to_user[receiver_buddy] = receiver

    buddy_set = [sender_buddy,receiver_buddy]

    ## get the ims
    for message_tag in root.iter('msgSent'):
        time_stamp = message_tag.find('timeStamp').text
        ## Getting only year-month-date from timestamp.
        time_stamp = datetime.fromtimestamp(int(time_stamp) / 1000.0).strftime("%m-%d-%yT%H:%M:%S")

        msg_buddy_receiver = message_tag.find('buddyName').text
        msg_receiver = buddy_to_user[msg_buddy_receiver]

        msg_buddy_sender = [buddy_set[0] if msg_buddy_receiver == buddy_set[1] else buddy_set[1]][0]
        msg_sender = buddy_to_user[msg_buddy_sender]

        text = message_tag.find('text').text

        if cfg.NOTICE_MESSAGE in text or cfg.DISCLAMER_MESSAGE_1 in text or cfg.DISCLAMER_MESSAGE_2 in text \
                or cfg.AUTO_RESPONSE in text :
            continue

        # print(classify_ims(text),text)

        classify = classify_ims(text)
        ## storing both buddy and encrypted name
        im_df = im_df.append({'sender': msg_sender,'sender_buddy':msg_buddy_sender, 'receiver': msg_receiver, 'receiver_buddy':msg_buddy_receiver,
                              'time_stamp': time_stamp, 'subject':'IM Message','content':text,'classify':classify},ignore_index=True)

    return im_df

def process_dictionary(im_file_weekly):
    """Function process the directories based on weeks."""
    count = 0
    name = multiprocessing.current_process().name
    print(name, 'Starting')
    for key in im_file_weekly.keys():
        im_df = pd.DataFrame(
            columns=['sender', 'sender_buddy', 'receiver', 'receiver_buddy', 'time_stamp', 'subject', 'content',
                     'classify'])
        for filename in im_file_weekly[key]:
            # print(filename)
            # start_time_file = time.time()
            try:
                # filename="/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/sample_files/Export_0x00000152_20060929045330_20060926235951_8838/IM_20090430105702_0x000001525e308dee062b8f6698cdb2307af881256487.eml"
                data = read_EML_file(filename)
                sender, receiver, time_stamp, subject, content = parse_eml_data(data)
                # im_df = parse_IM_data(content, im_df, sender, receiver)
                df = parse_IM_data(content, sender, receiver)
                im_df = pd.concat([im_df, df])
            except:
                print("IM file is not parsed properly")

            # print("Time between each files : {0}, {1}".format(time.time() - start_time_file,count))
            # count = count + 1
        print("Completed a week")
        im_df.to_csv(cfg.PROCESSED_DIR_PATH + "im_df_week" + str(key) + ".csv", index=False)
        im_df_list = [im_df]
        del im_df_list

def parse_all_files(pathlistSorted):
    ## To get the last part of directory


    start_date = date(2006, 8, 3)

    start_monday = (start_date - timedelta(days=start_date.weekday()))

    im_file_weekly = {}

    start_time_splitting_weeks = time.time()

    for dire in pathlistSorted:
        dir_list = dire.split('/')
        zipname = dir_list[-1]
        split_list = zipname.split('_')
        time_stamp = split_list[-2]
        day = int(time_stamp[6:8])
        month = int(time_stamp[4:6])
        year = int(time_stamp[0:4])

        try:
            curr_date = date(year,month,day)
            curr_monday = (curr_date - timedelta(days=curr_date.weekday()))

            week_num = int((curr_monday - start_monday).days/7)

            if week_num not in im_file_weekly.keys():
                im_file_weekly[week_num] = []


            for (dirpath, dirnames, filenames) in walk(dire):
                for filename in filenames:
                    if filename.startswith("IM_"):
                        im_file_weekly[week_num].append(dirpath + '/' + filename)
                    else:
                        continue
        except:
            print("Date not processed correctly")

    num_process = 1
    split_dictionaries = split_dict(im_file_weekly,num_process)
    # print(split_dictionaries)
    print("Completed splitting files in weeks {0}".format(time.time() - start_time_splitting_weeks))
    process_num = 0
    for dictionary in split_dictionaries:
        p = multiprocessing.Process(target=process_dictionary, args=(dictionary,),
                                    name="Process {0}".format(process_num))
        process_num = process_num + 1
        p.start()

def split_dfs(file_path,file_names):
    for file_name in file_names:
        if file_name.startswith("im_df"):
            df = pd.read_csv(file_path+file_name)
            df_group_list = df.groupby('classify')
            for classify, df_grouped in df_group_list:
                if(classify):
                    df_grouped.to_csv("./processed_business/"+file_name)
                else:
                    df_grouped.to_csv("./processed_personal/"+file_name)




def unique_member(directory):
    directory = directory.split("/")
    directory_name = directory[-3]

    print(directory_name)
    im_df = pd.read_csv(cfg.PROCESSED_DIR_PATH+"im_df_"+directory_name+".csv")

    # unique_im_members = im_df['sender'].append(im_df['receiver']).unique().tolist()
    unique_im_buddies = im_df['sender_buddy'].append(im_df['receiver_buddy']).unique().tolist()

    ## get unique member by date; group the data by date
    im_df_grouped = im_df.groupby('time_stamp')
    for date,group in im_df_grouped:
        unique_im_buddies_date = group['sender_buddy'].append(group['receiver_buddy']).unique().tolist()
        print("Date : {0} ; Unique IM Buddies : {1}".format(date,len(unique_im_buddies_date)))

    print(" Total Unique IM Buddies : {0}".format(len(unique_im_buddies)))

    # message_df = pd.read_csv(cfg.PROCESSED_DIR_PATH+"message_df_"+directory_name+".csv")
    # unique_message_members = message_df['sender'].append(message_df['receiver']).unique().tolist()
    # total_unique_members = set((unique_im_members+unique_message_members))

if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)

    # unique_member(cfg.DIRECTORY_PATH)
    ## Reads all the directories present

    # print("started running")
    # start_time_main = time.time()
    # # file_path = '/local/home/student/sainikhilmaram/hedgefund_data/data/'
    # # file_path = '/Users/sainikhilmaram/Desktop/nikhil_hedgefund/data'
    # file_path = '/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/sample_files/'
    #
    # pathlist = []
    # for (dirpath, dirnames, filenames) in walk(file_path):
    #     for dire in dirnames:
    #         pathlist.append(os.path.join(file_path, dire))
    #     break
    #
    # pathlistSorted = sorted(pathlist)
    # # print(pathlistSorted)
    # print("Completed sorting the directories and splitting them in {0}".format(time.time()-start_time_main))
    # parse_all_files(pathlistSorted)

    file_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/processed_files/"
    # file_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/processed_files/"
    file_list = []
    for(dirpath,dirnames,filnames) in walk(file_path):
        for filename in filnames:
            file_list.append(filename)

    split_dfs(file_path,file_list)


