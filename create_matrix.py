import config as cfg
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from os import walk
import os
import multiprocessing

import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'viridis'
import pickle
import misc

address_to_user_dict = {}
with open(
        "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/address_to_user_mapping.pkl",
        "rb") as handle:
# with open("./address_to_user_mapping.pkl","rb") as handle:
    address_to_user_dict = pickle.load(handle)

account_to_trader_dict,trader_to_account_dict = misc.parse_trader_book()
traders_list = trader_to_account_dict.keys()
print(traders_list)
def map_address_user(address):
    try:
        user = address_to_user_dict[address]
        return user
    except:
        return address.split('@')[0]
        # return address


def create_matrix(im_df):
    """Takes in a df and constructs message adjacency list and message matrix """
    im_columns = ['sender', 'sender_buddy', 'receiver', 'receiver_buddy', 'time_stamp', 'subject', 'content']

    im_df["sender_user"] = im_df["sender_buddy"].apply(lambda x : map_address_user(x))
    im_df["receiver_user"] = im_df["receiver_buddy"].apply(lambda x : map_address_user(x))

    ## Map
    unique_im_buddies = im_df['sender_buddy'].append(im_df['receiver_buddy']).unique().tolist()
    print("the number of unique buddues: %d" % len(unique_im_buddies))

    unique_im_buddies = im_df['sender_user'].append(im_df['receiver_user']).unique().tolist()
    print("the number of unique buddies: %d" % len(unique_im_buddies))

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
    message_matrix = np.zeros((unique_im_buddies_count,unique_im_buddies_count))
    # message_matrix = []
    message_adj_list = [set() for _ in range(unique_im_buddies_count)]

    for index, row in im_df.iterrows():
        # sender_buddy_idx = buddy_to_idx[row['sender_buddy']]
        sender_buddy_idx = buddy_to_idx[row['sender_user']]
        # receiver_buddy_idx = buddy_to_idx[row['receiver_buddy']]
        receiver_buddy_idx = buddy_to_idx[row['receiver_user']]
        message_matrix[sender_buddy_idx][receiver_buddy_idx] = message_matrix[sender_buddy_idx][receiver_buddy_idx] + 1
        message_adj_list[sender_buddy_idx].add(receiver_buddy_idx)
        # message_adj_list[receiver_buddy_idx].add(sender_buddy_idx)

    return message_matrix,message_adj_list,buddy_to_idx,idx_to_buddy


def create_graph(message_adj_list):
    """Creates graph w.r.t each day"""
    # for time, message_adj_list in message_adj_list_dict.items():
    G = nx.Graph()
    for src in range(len(message_adj_list)):
        for dest in message_adj_list[src]:
            G.add_edge(src, dest)

    pos = nx.spring_layout(G)

    num_nodes = len(G.nodes)
    colors = [1] * num_nodes

    nx.draw_networkx_nodes(G, pos, node_size=30,
                           node_color=colors, edgecolors='k',
                           cmap=plt.cm.Greys)

    nx.draw_networkx_edges(G, pos, alpha=0.5)

    plt.title("Graph ")
    # plt.savefig("./graphs/weighted_graph_{0}.png".format(time))  # save as png
    plt.show()  # display
    # plt.gcf().clear()



def plot_kcore_networkx(message_adj_list,k):
    """Plot the kcore nodes of the graph by the date"""
    # for time, message_adj_list in message_adj_list_dict.items():
    G = nx.Graph()
    for src in range(len(message_adj_list)):
        for dest in message_adj_list[src]:
            G.add_edge(src, dest)

    G.remove_edges_from(nx.selfloop_edges(G))
    kcore_G = nx.k_core(G,k)
    print(kcore_G.nodes)
    pos = nx.spring_layout(kcore_G)
    num_nodes = len(kcore_G.nodes)
    print("Number of k-core Nodes: {0}".format(num_nodes))
    colors = [1] * num_nodes
    nx.draw_networkx_nodes(kcore_G, pos, node_size=30,
                           node_color=colors, edgecolors='k',
                           cmap=plt.cm.Greys)

    nx.draw_networkx_edges(kcore_G, pos, alpha=0.5)
    # plt.title("{0}-core Graph for Date : {1}".format(k,time))
    plt.show()
        # break

def color_kcore_networkx(message_adj_list):
    """Colors the graph based on core level"""
    loop_count = 0
    # for time, message_adj_list in message_adj_list_dict.items():
    G = nx.Graph()
    for src in range(len(message_adj_list)):
        for dest in message_adj_list[src]:
            G.add_edge(src, dest)

    G.remove_edges_from(nx.selfloop_edges(G))
    colors = np.array(['1'] * len(G.nodes))
    pos = nx.spring_layout(G)

    ## Gives the max number of cores that graph can have
    max_core = 1
    for max_core in range(1,25):
        kcore_G = nx.k_core(G,max_core)
        # print(kcore_G.nodes)
        if(len(kcore_G.nodes) == 0):
            break
        colors[kcore_G.nodes] = max_core
        num_nodes = len(kcore_G.nodes)
        print("Number of {0}-core Nodes: {1}".format(max_core,num_nodes))

    # plt.title("Graph for Date : {0}".format(time))

    N = max_core-1
    # define the colormap
    cmap = plt.get_cmap('jet')
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # create the new map
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0, N, N + 1)
    scat = nx.draw_networkx_nodes(G, pos, node_size=30,
                                  node_color=colors, edgecolors='k',cmap=cmap)
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    cb = plt.colorbar(scat, spacing='proportional', ticks=bounds)
    cb.set_label('Custom cbar')
    plt.show()
    print("--------------------------------------------------------")

        # if(loop_count == 10):
        #     break
        # loop_count = loop_count + 1
        # break


def construct_kcore_networkx_salinas(message_matrix):

    message_matrix1 = np.zeros((len(message_matrix), len(message_matrix)))
    for i in range(len(message_matrix)):
        for j in range(i + 1, len(message_matrix)):
            message_matrix1[i][j] = message_matrix[i][j] + message_matrix[j][i]
            message_matrix1[j][i] = message_matrix1[i][j]

    # for time, message_adj_list in message_adj_list_dict.items():
    G = nx.Graph()
    for src in range(len(message_matrix1)):
        for dest in range(len(message_matrix1[0])):
            if src != dest and message_matrix1[src][dest] != 0:
                G.add_edge(src, dest, weight=message_matrix1[src][dest])

    degree = np.sum(message_matrix1, axis=1)
    G.remove_edges_from(nx.selfloop_edges(G))

    uniqueDegree = np.unique(degree)
    degrees = {}
    for i in range(len(degree)):
        degrees[i] = int(degree[i])

    # print(degrees)
    kcore_num_of_nodes_list = []
    kcore_number_list = []
    kcore_num_components_list = []
    kcore_largest_cc_num_nodes_list = []

    ## Gives the max number of cores that graph can have
    # for max_core in range(len(uniqueDegree)):

    for max_core in range(25):
        # print(uniqueDegree[max_core])
        # kcore_G = core.k_core(G, degrees, uniqueDegree[max_core])
        # kcore_G = nx.k_core(G, uniqueDegree[max_core])
        kcore_G = nx.k_core(G, max_core)

        kcore_num_of_nodes = len(kcore_G.nodes)
        subgraphs = nx.connected_component_subgraphs(kcore_G)
        kcore_num_components = len(list(subgraphs))
        kcore_num_components_list.append(kcore_num_components)

        if (kcore_num_of_nodes == 0):
            break

        kcore_num_of_nodes_list.append(kcore_num_of_nodes)
        # kcore_number_list.append(uniqueDegree[max_core])
        kcore_number_list.append(max_core)
        kcore_largest_cc = max(nx.connected_component_subgraphs(kcore_G), key=len)
        kcore_largest_cc_num_nodes = len(kcore_largest_cc.nodes)
        kcore_largest_cc_num_nodes_list.append(kcore_largest_cc_num_nodes)

        print("Number of {0}-core Nodes: {1}, Connected Components : {2}, largest CC Size: {3}"
              .format(max_core,kcore_num_of_nodes,kcore_num_components,kcore_largest_cc_num_nodes))
    # print(kcore_num_of_nodes_list)

    return kcore_number_list, kcore_num_of_nodes_list, kcore_num_components_list, kcore_largest_cc_num_nodes_list


def construct_weighted_kcore_networkx_salinas(message_matrix):

    message_matrix1 = np.zeros((len(message_matrix), len(message_matrix)))
    for i in range(len(message_matrix)):
        for j in range(i + 1, len(message_matrix)):
            message_matrix1[i][j] = message_matrix[i][j] + message_matrix[j][i]
            message_matrix1[j][i] = message_matrix1[i][j]

    # for time, message_adj_list in message_adj_list_dict.items():
    threshold = 4
    G = nx.Graph()
    for src in range(len(message_matrix1)):
        for dest in range(len(message_matrix1[0])):
            if src != dest and message_matrix1[src][dest] != 0:
                if (message_matrix1[src][dest] > threshold):
                    G.add_edge(src, dest, weight=message_matrix1[src][dest])

    degree = np.sum(message_matrix1, axis=1)

    uniqueDegree = np.unique(degree)
    degrees = {}
    for i in range(len(degree)):
        degrees[i] = int(degree[i])

    # print(degrees)
    kcore_num_of_nodes_list = []
    kcore_number_list = []
    kcore_num_components_list = []
    kcore_largest_cc_num_nodes_list = []

    ## Gives the max number of cores that graph can have
    # for max_core in range(len(uniqueDegree)):

    for max_core in range(25):
        # print(uniqueDegree[max_core])
        # kcore_G = core.k_core(G, degrees, uniqueDegree[max_core])
        # kcore_G = nx.k_core(G, uniqueDegree[max_core])
        kcore_G = nx.k_core(G, max_core)

        kcore_num_of_nodes = len(kcore_G.nodes)
        subgraphs = nx.connected_component_subgraphs(kcore_G)
        kcore_num_components = len(list(subgraphs))
        kcore_num_components_list.append(kcore_num_components)

        if (kcore_num_of_nodes == 0):
            break

        kcore_num_of_nodes_list.append(kcore_num_of_nodes)
        # kcore_number_list.append(uniqueDegree[max_core])
        kcore_number_list.append(max_core)
        kcore_largest_cc = max(nx.connected_component_subgraphs(kcore_G), key=len)
        kcore_largest_cc_num_nodes = len(kcore_largest_cc.nodes)
        kcore_largest_cc_num_nodes_list.append(kcore_largest_cc_num_nodes)

        print("Number of {0}-core Nodes: {1}, Connected Components : {2}, largest CC Size: {3}"
              .format(max_core,kcore_num_of_nodes,kcore_num_components,kcore_largest_cc_num_nodes))
    # print(kcore_num_of_nodes_list)

    return kcore_number_list, kcore_num_of_nodes_list, kcore_num_components_list, kcore_largest_cc_num_nodes_list


def trader_in_kcore_networkx_salinas(message_matrix,idx_to_buddy_dict,buddy_to_idx_dict):
    message_matrix1 = np.zeros((len(message_matrix), len(message_matrix)))
    for i in range(len(message_matrix)):
        for j in range(i + 1, len(message_matrix)):
            message_matrix1[i][j] = message_matrix[i][j] + message_matrix[j][i]
            message_matrix1[j][i] = message_matrix1[i][j]

    # for time, message_adj_list in message_adj_list_dict.items():
    G = nx.Graph()
    for src in range(len(message_matrix1)):
        for dest in range(len(message_matrix1[0])):
            if src != dest and message_matrix1[src][dest] != 0:
                G.add_edge(src, dest, weight=message_matrix1[src][dest])

    G.remove_edges_from(nx.selfloop_edges(G))

    for max_core in range(25):
        kcore_G = nx.k_core(G, max_core)
        # print(kcore_G.nodes)
        kcore_num_of_nodes = len(kcore_G.nodes)

        ## Get the buddies from indexes
        buddies_in_kcore = [idx_to_buddy_dict[node] for node in kcore_G.nodes]
        print(len(buddies_in_kcore))
        traders_in_kcore = list(set(buddies_in_kcore).intersection(traders_list))
        print(len(traders_in_kcore))
        ## check if buddies are traders
        if (kcore_num_of_nodes == 0):
            break




def return_kcore_nodes(message_adj_list_dict,buddy_to_idx_dict,idx_to_buddy_dict,k):
    """Returns kcore nodes of the graph"""
    kcore_nodes_dict = {}
    for time, message_adj_list in message_adj_list_dict.items():
        G = nx.Graph()
        for src in range(len(message_adj_list)):
            for dest in message_adj_list[src]:
                G.add_edge(src, dest)

        kcore_G = nx.k_core(G,k)
        # print(kcore_G.nodes)
        buddy_nodes = [idx_to_buddy_dict[time][node] for node in kcore_G.nodes]
        kcore_nodes_dict[time] = buddy_nodes
        print("Date : {0}, K : {1} , Unique Buddies Count : {2} "
              .format(time, k, len(buddy_nodes)))
        # break
    # print(kcore_nodes_dict)
    return kcore_nodes_dict

def unique_users(directory):
    """Gives number of unique users w.r.t each day"""
    total_df = pd.DataFrame()
    for (dirpath, dirnames, filenames) in walk(directory):
        for filename in filenames:
            if (filename.startswith("im_df")):
                df = pd.read_csv(dirpath+'/'+filename)
                total_df = total_df.append(df,ignore_index=True)

    total_df_grouped = total_df.groupby('time_stamp')
    for date,group in total_df_grouped:
        unique_im_buddies_date = group['sender_buddy'].append(group['receiver_buddy']).unique().tolist()
        # unique_im_buddies_date = group['sender'].append(group['receiver']).unique().tolist()
        print("Date : {0} ; Unique IM Buddies : {1}".format(date, len(unique_im_buddies_date)))

    total_im_buddies_unique = total_df['sender_buddy'].append(total_df['receiver_buddy']).unique().tolist()
    # total_im_buddies_unique = total_df['sender'].append(total_df['receiver']).unique().tolist()

    print("Total Unique Buddies : {0}".format(len(total_im_buddies_unique)))

def common_users(directory,k):
    """Common users between two days"""
    total_df = pd.DataFrame()
    for (dirpath, dirnames, filenames) in walk(directory):
        for filename in filenames:
            if (filename.startswith("im_df")):
                df = pd.read_csv(dirpath + '/' + filename)
                total_df = total_df.append(df, ignore_index=True)

    total_im_buddies_unique = total_df['sender_buddy'].append(total_df['receiver_buddy']).unique().tolist()
    # total_im_buddies_unique = total_df['sender'].append(total_df['receiver']).unique().tolist()

    print("Total Unique Buddies : {0}".format(len(total_im_buddies_unique)))

    total_df_grouped = total_df.groupby('time_stamp')
    # group1_df = total_df_grouped.get_group('02-22-07')
    # group2_df = total_df_grouped.get_group('02-23-07')
    #
    # group1_buddies_unique = group1_df['sender_buddy'].append(group1_df['receiver_buddy']).unique().tolist()
    # group2_buddies_unique = group2_df['sender_buddy'].append(group2_df['receiver_buddy']).unique().tolist()
    #


    message_matrix_dict, message_adj_list_dict, buddy_to_idx_dict, idx_to_buddy_dict = create_matrix_dict(total_df)
    kcore_nodes_dict = return_kcore_nodes(message_adj_list_dict, buddy_to_idx_dict, idx_to_buddy_dict, k)
    group1_buddies_unique = kcore_nodes_dict['02-22-07']
    group2_buddies_unique = kcore_nodes_dict['02-23-07']

    common_buddies = set(group1_buddies_unique).intersection(set(group2_buddies_unique))
    print("K :{3}, Group1 Unique Buddies : {0} , Group2 Unique Buddies : {1} , Common Buddies : {2}".
          format(len(group1_buddies_unique),len(group2_buddies_unique),len(common_buddies),k))

    total_unique_nodes= list()
    for time,nodes in kcore_nodes_dict.items():
        total_unique_nodes.extend(nodes)

    total_unique_nodes = set(total_unique_nodes)

    print("K : {0}, Total Unique Nodes: {1}".format(k,len(total_unique_nodes)))


def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))



def multiprocess_salinas(dir_path,filenames,output_path):
    for filename in filenames:
        if filename.startswith("im_df"):
            weeknum = filename.split('.')[0][10:]
            print(weeknum)
            file_path = os.path.join(dir_path, filename)
            print(file_path)
            df = pd.read_csv(file_path)
            message_matrix, message_adj_list, buddy_to_idx, idx_to_buddy = create_matrix(df)
            ## Unweighted
            kcore_number_list, kcore_num_of_nodes_list, kcore_num_components_list, kcore_largest_cc_num_nodes_list = construct_kcore_networkx_salinas(
                message_matrix)

            # kcore_number_list, kcore_num_of_nodes_list, kcore_num_components_list, kcore_largest_cc_num_nodes_list = construct_weighted_kcore_networkx_salinas(
            #     message_matrix)

            with open(output_path + "/kcore_number_week{0}.csv".format(weeknum), "w") as myfile:
                for ele in kcore_number_list:
                    myfile.write("%d" % ele)
                    myfile.write(",")
                myfile.write("\n")
            myfile.close()

            with open(output_path + "/kcore_num_of_nodes_week{0}.csv".format(weeknum), "w") as myfile:
                for ele in kcore_num_of_nodes_list:
                    myfile.write("%d" % ele)
                    myfile.write(",")
                myfile.write("\n")
            myfile.close()

            with open(output_path + "/kcore_num_components_week{0}.csv".format(weeknum), "w") as myfile:
                for ele in kcore_num_components_list:
                    myfile.write("%d" % ele)
                    myfile.write(",")
                myfile.write("\n")
            myfile.close()

            with open(output_path + "/kcore_largest_cc_num_nodes_week{0}.csv".format(weeknum), "w") as myfile:
                for ele in kcore_largest_cc_num_nodes_list:
                    myfile.write("%d" % ele)
                    myfile.write(",")
                myfile.write("\n")
            myfile.close()




if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    ## message matrix contains edge weight about number of messages exchanged. It gives information of a directed graph.


    # df = pd.read_csv(cfg.PROCESSED_DIR_PATH + "im_df_Export_0x00000152_20070222130307_20070223175543_17075.csv")
    # df = pd.read_csv(
    #     "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/processed_files/im_df_week78.csv")
    # message_matrix_dict,message_adj_list_dict,buddy_to_idx_dict,idx_to_buddy_dict = create_matrix_dict(df)
    # message_matrix, message_adj_list, buddy_to_idx, idx_to_buddy = create_matrix(df)


    # plot_kcore_networkx(message_adj_list,1)
    # construct_k_core_degrees(message_adj_list_dict,3)
    # color_kcore_networkx(message_adj_list)

    # kcore_nodes_dict = return_kcore_nodes(message_adj_list_dict,buddy_to_idx_dict,idx_to_buddy_dict,2)
    # unique_users(cfg.PROCESSED_DIR_PATH)
    # common_users(cfg.PROCESSED_DIR_PATH,1)

    df = pd.read_csv("/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/processed_files/im_df_week76.csv")
    message_matrix, message_adj_list, buddy_to_idx, idx_to_buddy = create_matrix(df)
    trader_in_kcore_networkx_salinas(message_matrix,idx_to_buddy,buddy_to_idx)

    # dir_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/processed_files/"

    # dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/processed_files/"
    # output_path = "./kcore/"
    #
    # file_names_list = []
    # for (dirpath, dirnames, filenames) in walk(dir_path):
    #     for filename in filenames:
    #         file_names_list.append(filename)
    #
    # num_process = 16
    # print(file_names_list)
    # chunked_file_names_list = list(chunker_list(file_names_list,num_process))
    # print(chunked_file_names_list)
    #
    # for file_names in chunked_file_names_list:
    #     p = multiprocessing.Process(target=multiprocess_salinas, args=(dir_path,file_names,output_path,))
    #     p.start()
    #
    #
    # dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/processed_business/"
    # output_path = "./kcore_business/"
    #
    # file_names_list = []
    # for (dirpath, dirnames, filenames) in walk(dir_path):
    #     for filename in filenames:
    #         file_names_list.append(filename)
    #
    # num_process = 16
    # print(file_names_list)
    # chunked_file_names_list = list(chunker_list(file_names_list, num_process))
    # print(chunked_file_names_list)
    #
    # for file_names in chunked_file_names_list:
    #     p = multiprocessing.Process(target=multiprocess_salinas, args=(dir_path, file_names, output_path,))
    #     p.start()
    #
    #
    # dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/processed_personal/"
    # output_path = "./kcore_personal/"
    #
    # file_names_list = []
    # for (dirpath, dirnames, filenames) in walk(dir_path):
    #     for filename in filenames:
    #         file_names_list.append(filename)
    #
    # num_process = 16
    # print(file_names_list)
    # chunked_file_names_list = list(chunker_list(file_names_list, num_process))
    # print(chunked_file_names_list)
    #
    # for file_names in chunked_file_names_list:
    #     p = multiprocessing.Process(target=multiprocess_salinas, args=(dir_path, file_names, output_path,))
    #     p.start()