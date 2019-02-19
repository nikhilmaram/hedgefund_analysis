"""To check total users in the dataset"""

import pickle

import pandas as pd
import  os


address_to_user_dict = {}
# with open(
#         "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/address_to_user_mapping.pkl",
#         "rb") as handle:
with open("./address_to_user_mapping.pkl","rb") as handle:
    address_to_user_dict = pickle.load(handle)

def map_address_user(address):
    try:
        user = address_to_user_dict[address]
        return user
    except:
        return address.split('@')[0]


def all_users(dir_path,filename,all_user_list):
    if filename.startswith("im_df"):
        file_path = os.path.join(dir_path, filename)
        print(file_path)
        im_df = pd.read_csv(file_path)
        im_df["sender_user"] = im_df["sender_buddy"].apply(lambda x: map_address_user(x))
        im_df["receiver_user"] = im_df["receiver_buddy"].apply(lambda x: map_address_user(x))
        unique_im_buddies = im_df['sender_user'].append(im_df['receiver_user']).unique().tolist()
        all_user_list = list(set(unique_im_buddies + all_user_list))
    return all_user_list


if __name__ == "__main__":

    dir_path = "./processed_files/"
    output_file = "./unique_users.csv"

    file_names_list = []
    for (dirpath, dirnames, filenames) in os.walk(dir_path):
        for filename in filenames:
            file_names_list.append(filename)
    all_user_list = []

    for filename in file_names_list:
        all_user_list = all_users(dir_path,filename,all_user_list)

    with open(output_file,"w") as f:
        for user in all_user_list:
            f.write(user+"\n")

        f.close()

