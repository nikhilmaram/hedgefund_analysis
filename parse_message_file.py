import config as cfg
import datetime
import eml_parser
from os import walk


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial


# # raw_email=""
# with open(cfg.DIRECTORY_PATH+cfg.MSG_EML_FILE, 'rb') as fhdl:
#     raw_email = fhdl.read()
#     # print(raw_email)
#
#     parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email,include_raw_body=True)
#     print(parsed_eml)
#
#     # print(json.dumps(parsed_eml, default=json_serial))
#     f = open('temp.json','w')
#     json.dump(parsed_eml,f,ensure_ascii=False,default=json_serial)

"""In case there are multiple messages in a email"""

class message_class:
    def __init__(self,text,sender,subject,time_stamp):
        self.text = text
        self.sender = sender
        self.receivers = []
        self.subject = subject
        self.time_stamp = time_stamp

    def add_receiver(self,receiver):
        self.receivers.append(receiver)

    def __str__(self):
        return "{{ 'Sender' : {0} , 'Receiver' : {1} , 'time_stamp' : {2} \n  'Subject' : {3} \n  'Content': {4} }}". \
            format(self.sender, self.receivers[0], self.time_stamp, self.subject, self.text)

    def __repr__(self):
        return "{{ 'Sender' : {0} , 'Receiver' : {1} , 'time_stamp' : {2} \n  'Subject' : {3} \n  'Content': {4} }}". \
            format(self.sender, self.receivers[0], self.time_stamp, self.subject, self.text)


class message_file_class:
    def __init__(self):
        self.messages = []

    def add_message(self,message):
        self.messages.append(message)

    def __str__(self):
        return "Messages : {0}".format(self.messages)

    def __repr__(self):
        return "Messages : {0}".format(self.messages)



def read_MESSAGE_EML_file(eml_file):
    with open(eml_file, 'rb') as fhdl:
        raw_email = fhdl.read()
        # print(raw_email)

        parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email, include_raw_body=True)
        # print(parsed_eml)

        # temp_file = open('temp.json', 'w')
        # json.dump(parsed_eml, temp_file, ensure_ascii=False, default=json_serial)

        return parsed_eml


def parse_MESSAGE_data(data):

    ## first item in the 'body' value will be actual email.
    content = data["body"][0]["content"]

    ## currently taking only one element
    subject = data["header"]["header"]["subject"][0]


    if "x-sender" in data["header"]["header"].keys():
        sender = data["header"]["header"]["x-sender"][0]
    else:
        sender = data["header"]["header"]["from"][0]
    if "x-receiver" in data["header"]["header"].keys():
        receiver = data["header"]["header"]["x-receiver"][0]
    else:
        receiver = data["header"]["header"]["to"][0]

    time_stamp = data["header"]["header"]["date"][0]

    message_obj = message_class(content,sender,subject,time_stamp)
    message_obj.add_receiver(receiver)

    message_file_obj = message_file_class()
    message_file_obj.add_message(message_obj)

    # print(message_obj)
    # print(message_file_obj)
    return message_file_obj

def iterate_through_files_in_directory(directory):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(directory):
        # print(dirpath)
        for filename in filenames:
            if filename.startswith("Message_"):
                file_list.append(filename)

    message_obj_list={}
    for file in file_list:
        # print(file)
        data = read_MESSAGE_EML_file(cfg.DIRECTORY_PATH+'/'+file)
        message_obj = parse_MESSAGE_data(data)
        message_obj_list[file] = message_obj

    print(message_obj_list)
    return message_obj_list

if __name__ == "__main__":
    data = read_MESSAGE_EML_file(cfg.DIRECTORY_PATH+cfg.MSG_EML_FILE)
    # data = read_MESSAGE_EML_file(cfg.DIRECTORY_PATH + cfg.BLOOMBERG_EML_FILE)
    parse_MESSAGE_data(data)
    # iterate_through_files_in_directory(cfg.DIRECTORY_PATH)