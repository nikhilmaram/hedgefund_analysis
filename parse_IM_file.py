import config as cfg

import xml.etree.ElementTree as ET
import re
from os import walk



class im_file_class:
    def __init__(self,start_time,end_time):
        self.buddy_names=[]
        self.ims=[]
        self.start_time = start_time
        self.end_time = end_time

    def add_message(self,im):
        self.ims.append(im)
    def add_buddy(self,buddy_name):
        self.buddy_names.append(buddy_name)

    def __str__(self):
        return "{{'startime': {0} , 'endtime' : {1} ,'buddy' : {2}, 'ims' = {3} }}"\
            .format(self.start_time,self.end_time,self.buddy_names, self.ims)
    def __repr__(self):
        return "{{'startime': {0} , 'endtime' : {1} ,'buddy' : {2}, 'ims' = {3} }}"\
            .format(self.start_time,self.end_time,self.buddy_names, self.ims)



class im_class:
    def __init__(self,time_stamp,sender,receiver,text):
        self.time_stamp = time_stamp
        self.sender = sender
        self.receiver = receiver
        self.text = text

    def __str__(self):
        return "{{'time_stamp' : {0}, 'sender' : {1} , 'receiver' : {2} , 'text' = {3} }}".\
            format(self.time_stamp,self.sender,self.receiver,self.text)

    def __repr__(self):
        return "{{'time_stamp' : {0}, 'sender' : {1} , 'receiver' : {2} , 'text' = {3} }}".\
            format(self.time_stamp,self.sender,self.receiver,self.text)



def read_IM_EML_file(eml_file):
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
    return data

def parse_IM_data(data):

    ## Write into a temporary file to check intermediata XML data
    # file_write = open('temp.xml','w')
    # file_write.write(data)
    # file_write.close()

    ## parse the XML data
    root = ET.fromstring(data)
    # print(root.tag)

    start_time = root.find('startTime').text
    end_time = root.find('endTime').text
    # print(start_time) ; print(end_time)

    xml_obj = im_file_class(start_time,end_time)

    ## get the buddy names
    buddy_set = set()
    for buddy_tag in root.iter('buddyName'):
        buddy_set.add(buddy_tag.text)
    # print(buddy_set)
    ## add buddy names to the object
    for buddy in buddy_set:
        xml_obj.add_buddy(buddy)


    ## get the ims
    for message_tag in root.iter('msgSent'):
        time_stamp = message_tag.find('timeStamp').text
        receiver = message_tag.find('buddyName').text
        text = message_tag.find('text').text
        sender = [x for x in buddy_set if x!= receiver][0]
        if(text == cfg.NOTICE_MESSAGE):
            continue
        im = im_class(time_stamp,sender,receiver,text)
        # print(im)
        ## Add im to the xml class object
        xml_obj.add_message(im)

    # print(xml_obj)
    return xml_obj


def iterate_through_files_in_directory(directory):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(directory):
        # print(dirpath)
        for filename in filenames:
            if filename.startswith("IM_"):
                file_list.append(filename)

    im_obj_list={}
    for file in file_list:
        print(file)
        data = read_IM_EML_file(cfg.DIRECTORY_PATH+'/'+file)
        im_obj = parse_IM_data(data)
        im_obj_list[file] = im_obj

    print(im_obj_list)
    return im_obj_list




if __name__ == "__main__":
    # data = read_IM_EML_file(cfg.DIRECTORY_PATH+cfg.IM_EML_FILE)
    # parse_IM_data(data)
    iterate_through_files_in_directory(cfg.DIRECTORY_PATH)
