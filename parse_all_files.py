import config as cfg
import datetime
import eml_parser
import json
import os
import re
from os import walk
import pandas as pd
import xml.etree.ElementTree as ET

import parse_message_file


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

def read_EML_file(eml_file):
    with open(eml_file, 'rb') as fhdl:
        raw_email = fhdl.read()
        # print(raw_email)

        parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email, include_raw_body=True)

        temp_file = open('temp.json', 'w')
        json.dump(parsed_eml, temp_file, ensure_ascii=False, default=json_serial)

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

def parse_IM_data(data,im_df,sender,receiver):

    # # Write into a temporary file to check intermediata XML data
    # file_write = open('temp.xml','w')
    # file_write.write(data)
    # file_write.close()

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

        msg_buddy_receiver = message_tag.find('buddyName').text
        msg_receiver = buddy_to_user[msg_buddy_receiver]

        msg_buddy_sender = [buddy_set[0] if msg_buddy_receiver == buddy_set[1] else buddy_set[1]][0]
        msg_sender = buddy_to_user[msg_buddy_sender]

        text = message_tag.find('text').text
        if cfg.NOTICE_MESSAGE in text:
            continue

        ## storing both buddy and encrypted name
        im_df = im_df.append({'sender': msg_sender,'sender_buddy':msg_buddy_sender, 'receiver': msg_receiver, 'receiver_buddy':msg_buddy_receiver,
                              'time_stamp': time_stamp, 'subject':'IM Message','content':text},ignore_index=True)

    return im_df

def parse_all_files(directory):
    message_file_list = []
    im_file_list = []
    bloomberg_file_list = []
    for (dirpath, dirnames, filenames) in walk(directory):
        # print(dirpath)
        for filename in filenames:
            if filename.startswith("Message_"):
                message_file_list.append(dirpath+'/'+filename)
            elif (filename.startswith("IM_")):
                im_file_list.append(dirpath+'/'+filename)
            elif(filename.startswith("Bloomberg_")):
                bloomberg_file_list.append(dirpath+'/'+filename)
            else:
                # print("some unknown file")
                continue

    im_df = pd.DataFrame(columns=['sender','sender_buddy','receiver','receiver_buddy','time_stamp','subject','content'])
    message_df = pd.DataFrame(columns=['sender', 'receiver', 'time_stamp', 'subject', 'content'])
    bloomberg_df = pd.DataFrame(columns=['sender', 'receiver', 'time_stamp', 'subject', 'content'])
    ## append all im messages to a dataframe


    ## Processing Messages

    for filename in bloomberg_file_list:
        # print(filename)
        try:
            data = read_EML_file(filename)
            sender, receiver, time_stamp, subject, content = parse_eml_data(data)
            ## Add the message files which have IM
            if(subject.startswith(cfg.IM_MESSAGE)):
                # print("Message contains an IM file")
                bloomberg_file_list.remove(filename)
                im_file_list.append(filename)
                continue
            ## The actual content is hidden to reduce the space.
            bloomberg_df = bloomberg_df.append({'sender': sender, 'receiver': receiver,
                                  'time_stamp': time_stamp, 'subject': subject, 'content': 'Test Content'}, ignore_index=True)

        except:
            print("EML file is not parsed properly")
    num_bloomberg_files = len(bloomberg_file_list)
    unique_bloomberg_members = len(bloomberg_df['sender'].append(bloomberg_df['receiver']).unique())
    print("Bloomberg Files : {0} , Unique Message Members : {1}".format(num_bloomberg_files, unique_bloomberg_members))

    bloomberg_df.to_csv(cfg.PROCESSED_DIR_PATH+"bloomberg_df.csv",index=False)

    ## To delete data frame to free up memory
    bloomberg_df_list = [bloomberg_df]
    del bloomberg_df
    del bloomberg_df_list



    ## Processing Messages

    for filename in message_file_list:
        # print(filename)
        try:
            data = read_EML_file(filename)
            sender, receiver, time_stamp, subject, content = parse_eml_data(data)
            ## Add the message files which have IM
            if(subject.startswith(cfg.IM_MESSAGE)):
                # print("Message contains an IM file")
                message_file_list.remove(filename)
                im_file_list.append(filename)
                continue
            ## The actual content is hidden to reduce the space.
            message_df = message_df.append({'sender': sender, 'receiver': receiver,
                                  'time_stamp': time_stamp, 'subject': subject, 'content': 'Test Content'}, ignore_index=True)

        except:
            print("EML file is not parsed properly")
    num_message_files = len(message_file_list)
    unique_message_members = len(message_df['sender'].append(message_df['receiver']).unique())
    print("Message Files : {0} , Unique Message Members : {1}".format(num_message_files, unique_message_members))

    message_df.to_csv(cfg.PROCESSED_DIR_PATH+"message_df.csv",index=False)

    ## To delete data frame to free up memory
    message_df_list = [message_df]
    del message_df
    del message_df_list

    ## Processing IMs
    for filename in im_file_list:
        # print(filename)
        data = read_EML_file(filename)
        sender, receiver, time_stamp, subject, content = parse_eml_data(data)
        im_df = parse_IM_data(content, im_df, sender, receiver)

    # print(im_df)

    number_im_files = len(im_file_list)
    unique_im_members = len(im_df['sender'].append(im_df['receiver']).unique())
    print("IM Files : {0} , Unique IM Members : {1}".format(number_im_files, unique_im_members))

    im_df.to_csv(cfg.PROCESSED_DIR_PATH+"im_df.csv",index=False)
    im_df_list = [im_df]
    del im_df
    del im_df_list


def unique_member():
    im_df = pd.read_csv(cfg.PROCESSED_DIR_PATH+"im_df.csv")
    message_df = pd.read_csv(cfg.PROCESSED_DIR_PATH+"message_df.csv")
    unique_im_members = im_df['sender'].append(im_df['receiver']).unique().tolist()
    unique_im_buddies = im_df['sender_buddy'].append(im_df['receiver_buddy']).unique().tolist()
    unique_message_members = message_df['sender'].append(message_df['receiver']).unique().tolist()

    total_unique_members = set((unique_im_members+unique_message_members))

    print("Unique IM Members : {0}, Unique Message Members : {1}, Unique Total Members : {2},unique IM buddies : {3}"
          .format(len(unique_im_members),len(unique_message_members),len(total_unique_members),len(unique_im_buddies)))



if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    parse_all_files(cfg.DIRECTORY_PATH)
    # unique_member()