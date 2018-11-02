import config as cfg

import xml.etree.ElementTree as ET
import re
from os import walk



class xml_class:
    def __init__(self,start_time,end_time):
        self.buddy_names=[]
        self.messages=[]
        self.start_time = start_time
        self.end_time = end_time

    def add_message(self,message):
        self.messages.append(message)
    def add_buddy(self,buddy_name):
        self.buddy_names.append(buddy_name)

    def __str__(self):
        return "startime: {0} , endtime : {1} ,buddy : {2}, messages = {3}"\
            .format(self.start_time,self.end_time,self.buddy_names, self.messages)



class message_class:
    def __init__(self,time_stamp,sender,receiver,text):
        self.time_stamp = time_stamp
        self.sender = sender
        self.receiver = receiver
        self.text = text

    def __str__(self):
        return "time_stamp : {0}, sender : {1} , receiver : {2} , text = {3}".\
            format(self.time_stamp,self.sender,self.receiver,self.text)

    # def __repr__(self):
    #     return "time_stamp : {0}, sender : {1} , receiver : {2} , text = {3}". \
    #         format(self.time_stamp, self.sender, self.receiver, self.text)


def read_EML_file(eml_file):
    """We will read the EML file and extract the XML tree.
     Because EML file has extra text information which causes XML parser to fail."""

    ## Read the file data into string
    with open(eml_file, 'r') as myfile:
        file_data = myfile.read()



    ## match the pattern
    pattern = "(\<interaction\>)(.*)(\<\/interaction\>)"
    m = re.search(pattern, file_data, re.DOTALL)

    ## Add the XML header so XML parser can work
    data = cfg.XML_HEADER + m.group(0)
    # print(data)

    file_write = open('temp.xml','w')
    file_write.write(data)
    file_write.close()
    ## parse the XML file
    root = ET.fromstring(data)
    # print(root.tag)

    start_time = root.find('startTime').text
    end_time = root.find('endTime').text
    # print(start_time) ; print(end_time)

    xml_obj = xml_class(start_time,end_time)

    ## get the buddy names
    buddy_set = set()
    for buddy_tag in root.iter('buddyName'):
        buddy_set.add(buddy_tag.text)
    # print(buddy_set)
    ## add buddy names to the object
    for buddy in buddy_set:
        xml_obj.add_buddy(buddy)


    ## get the messages
    for message_tag in root.iter('msgSent'):
        time_stamp = message_tag.find('timeStamp').text
        receiver = message_tag.find('buddyName').text
        text = message_tag.find('text').text
        sender = [x for x in buddy_set if x!= receiver][0]
        if(text == cfg.NOTICE_MESSAGE):
            continue
        message = message_class(time_stamp,sender,receiver,text)
        print(message)
        ## Add message to the xml class object
        xml_obj.add_message(message)

    print(xml_obj)
    return xml_obj


def iterate_through_files_in_directory(directory):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(directory):
        print(dirpath)
        for filename in filenames:
            if filename.startswith("IM_"):
                file_list.append(filename)

    eml_obj_list=[]
    for file in file_list:
        print(file)
        eml_obj_list.append(read_EML_file(cfg.DIRECTORY_PATH+'/'+file))
    print(eml_obj_list)




if __name__ == "__main__":
    read_EML_file(cfg.DIRECTORY_PATH+cfg.EML_FILE_NAME)
    # iterate_through_files_in_directory(cfg.DIRECTORY_PATH)
