import numpy as np
import pandas as pd
import csv
import os
import multiprocessing

def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))

def edge_distribution(im_df):
    """Takes in a df and constructs a dictionary which has number of times a degree has repeated """

    unique_im_buddies = im_df['sender_buddy'].append(im_df['receiver_buddy']).unique().tolist()
    print("the number of unique buddues: %d" % len(unique_im_buddies))

    buddy_to_idx = {}
    idx_to_buddy = {}

    ## Assign index to each buddy
    count = 0
    for buddy in unique_im_buddies:
        buddy_to_idx[buddy] = count
        idx_to_buddy[count] = buddy
        count = count + 1

    # print(buddy_to_idx)
    unique_im_buddies_count = len(unique_im_buddies)
    message_matrix = np.zeros((unique_im_buddies_count, unique_im_buddies_count))

    for index, row in im_df.iterrows():
        sender_buddy_idx = buddy_to_idx[row['sender_buddy']]
        # sender_buddy_idx = buddy_to_idx[row['sender']]
        receiver_buddy_idx = buddy_to_idx[row['receiver_buddy']]
        # receiver_buddy_idx = buddy_to_idx[row['receiver']]
        message_matrix[sender_buddy_idx][receiver_buddy_idx] = message_matrix[sender_buddy_idx][receiver_buddy_idx] + 1
        message_matrix[receiver_buddy_idx][sender_buddy_idx] = message_matrix[receiver_buddy_idx][sender_buddy_idx] + 1

    degree_count_dict = {}
    # print(message_matrix)

    for i in range(unique_im_buddies_count):
        for j in range(i,unique_im_buddies_count):
            degree = message_matrix[i][j]
            degree_count_dict[degree] = degree_count_dict.get(degree,0) + 1
    # print(degree_count_dict)
    return degree_count_dict


def multiprocess_salinas(dir_path,filenames,output_path):
    for filename in filenames:
        if filename.startswith("im_df"):
            weeknum = filename.split('.')[0][10:]
            print(weeknum)
            file_path = os.path.join(dir_path, filename)
            print(file_path)
            df = pd.read_csv(file_path)
            degree_count_dict = edge_distribution(df)

            with open(output_path + "/edge_distribution_week{0}.csv".format(weeknum), "w") as myfile:
                w = csv.writer(myfile)
                for key,val in degree_count_dict.items():
                    w.writerow([key,val])
            myfile.close()

if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    dir_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/processed_files/"
    # dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/processed_business/"
    output_path = "./edge_distribution/"



    file_names_list = []
    for (dirpath, dirnames, filenames) in os.walk(dir_path):
        for filename in filenames:
            file_names_list.append(filename)

    num_process = 1
    # print(file_names_list)
    chunked_file_names_list = list(chunker_list(file_names_list,num_process))
    print(chunked_file_names_list)

    for file_names in chunked_file_names_list:
        p = multiprocessing.Process(target=multiprocess_salinas, args=(dir_path,file_names,output_path,))
        p.start()