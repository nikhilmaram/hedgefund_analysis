import config as cfg
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from os import walk

import matplotlib.style
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'viridis'

def create_df(directory):
    """Creates a data frame by reading all im files in processed directory"""
    # im_df = pd.read_csv(file)
    total_df = pd.DataFrame()
    for (dirpath, dirnames, filenames) in walk(directory):
        for filename in filenames:
            if (filename.startswith("im_df")):
                df = pd.read_csv(dirpath+'/'+filename)
                total_df = total_df.append(df,ignore_index=True)
    total_im_buddies_unique = total_df['sender_buddy'].append(total_df['receiver_buddy']).unique().tolist()
    # total_im_buddies_unique = total_df['sender'].append(total_df['receiver']).unique().tolist()

    print("Total Unique Buddies : {0}".format(len(total_im_buddies_unique)))
    return total_df

def create_matrix(im_df):
    """Takes in a df and constructs message adjaceny list and message matrix grouped by date"""
    im_columns = ['sender', 'sender_buddy', 'receiver', 'receiver_buddy', 'time_stamp', 'subject', 'content']

    message_adj_list_dict = {}
    message_matrix_dict = {}
    buddy_to_idx_dict = {}
    idx_to_buddy_dict = {}

    for time, df in im_df.groupby('time_stamp'):
        unique_im_buddies = df['sender_buddy'].append(df['receiver_buddy']).unique().tolist()
        # unique_im_buddies = df['sender'].append(df['receiver']).unique().tolist()

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

        print("Date : {0}, Unique Buddies Count : {1}, Number of Messages : {2} "
              .format(time,unique_im_buddies_count,len(df.index)))

        # message_matrix = np.zeros((unique_im_buddies_count,unique_im_buddies_count))
        message_matrix = []
        message_adj_list = [set() for _ in range(unique_im_buddies_count)]

        for index, row in df.iterrows():
            sender_buddy_idx = buddy_to_idx[row['sender_buddy']]
            # sender_buddy_idx = buddy_to_idx[row['sender']]
            receiver_buddy_idx = buddy_to_idx[row['receiver_buddy']]
            # receiver_buddy_idx = buddy_to_idx[row['receiver']]
            # message_matrix[sender_buddy_idx][receiver_buddy_idx] = message_matrix[sender_buddy_idx][receiver_buddy_idx] + 1
            message_adj_list[sender_buddy_idx].add(receiver_buddy_idx)
            message_adj_list[receiver_buddy_idx].add(sender_buddy_idx)

        ## Saving the array to text
        # np.savetxt('matrix.txt', message_matrix, delimiter=' ',fmt='%d')

        # print("Highest Number of edges : {0}".format(max(map(max,message_matrix))))
        message_adj_list_dict[time] = message_adj_list
        message_matrix_dict[time] = message_matrix
        buddy_to_idx_dict[time] = buddy_to_idx
        idx_to_buddy_dict[time] = idx_to_buddy

    return message_matrix_dict,message_adj_list_dict,buddy_to_idx_dict,idx_to_buddy_dict

def create_graph(message_adj_list_dict):
    """Creates graph w.r.t each day"""
    for time, message_adj_list in message_adj_list_dict.items():
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

        plt.title("Graph for Date : {0}".format(time))
        # plt.axis('off')
        plt.savefig("./graphs/weighted_graph_{0}.png".format(time))  # save as png
        plt.show()  # display
        # plt.gcf().clear()

def construct_k_core_degrees(message_adj_list_dict,k):
    """Remove all nodes whose degree is less than k"""
    for time, message_adj_list in message_adj_list_dict.items():
        G = nx.Graph()

        degree_nodes = np.array([len(message_adj_list[i]) for i in range(len(message_adj_list))])
        print(len(degree_nodes))
        more_than_k_nodes = []

        for i in range(len(degree_nodes)):
            if (degree_nodes[i] >= k):
                more_than_k_nodes.append(i)
        # print(more_than_k_nodes)

        ## Add an edge between the nodes if only degree of both nodes are greater than or equal to k.
        for src in more_than_k_nodes:
            for dest in message_adj_list[src]:
                if dest in more_than_k_nodes:
                    G.add_edge(src, dest)

        pos = nx.spring_layout(G)

        num_nodes = len(G.nodes)
        colors = [1] * num_nodes
        print(num_nodes)

        nx.draw_networkx_nodes(G, pos, node_size=30,
                               node_color=colors, edgecolors='k',
                               cmap=plt.cm.Greys)

        nx.draw_networkx_edges(G, pos, alpha=0.5)

        plt.title("Graph for Date : {0}".format(time))
        # plt.axis('off')
        # plt.savefig("./graphs/weighted_graph_{0}.png".format(time))  # save as png
        plt.show()  # display
        plt.gcf().clear()
        break

def construct_kcore_networkx(message_adj_list_dict,k):
    """Plot the kcore nodes of the graph by the date"""
    for time, message_adj_list in message_adj_list_dict.items():
        G = nx.Graph()
        for src in range(len(message_adj_list)):
            for dest in message_adj_list[src]:
                G.add_edge(src, dest)

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
        plt.title("{0}-core Graph for Date : {1}".format(k,time))
        plt.show()
        break

def color_kcore_networkx(message_adj_list_dict):
    """Colors the graph based on core level"""
    loop_count = 0
    for time, message_adj_list in message_adj_list_dict.items():
        G = nx.Graph()
        for src in range(len(message_adj_list)):
            for dest in message_adj_list[src]:
                G.add_edge(src, dest)


        colors = np.array(['1'] * len(G.nodes))
        pos = nx.spring_layout(G)

        ## Gives the max number of cores that graph can have
        max_core = 1
        for max_core in range(1,100):
            kcore_G = nx.k_core(G,max_core)
            # print(kcore_G.nodes)
            if(len(kcore_G.nodes) == 0):
                break
            colors[kcore_G.nodes] = max_core
            num_nodes = len(kcore_G.nodes)
            print("Number of {0}-core Nodes: {1}".format(max_core,num_nodes))

        plt.title("Graph for Date : {0}".format(time))

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

        if(loop_count == 10):
            break
        loop_count = loop_count + 1
        # break

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


    message_matrix_dict, message_adj_list_dict, buddy_to_idx_dict, idx_to_buddy_dict = create_matrix(total_df)
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

if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    ## message matrix contains edge weight about number of messages exchanged. It gives information of a directed graph.
    # df = create_df(cfg.PROCESSED_DIR_PATH)
    df = pd.read_csv(cfg.PROCESSED_DIR_PATH + "im_df_Export_0x00000152_20070222130307_20070223175543_17075.csv")
    message_matrix_dict,message_adj_list_dict,buddy_to_idx_dict,idx_to_buddy_dict = create_matrix(df)

    # create_graph(message_adj_list_dict)
    # construct_kcore_networkx(message_adj_list_dict,3)
    # construct_k_core_degrees(message_adj_list_dict,3)
    color_kcore_networkx(message_adj_list_dict)
    # kcore_nodes_dict = return_kcore_nodes(message_adj_list_dict,buddy_to_idx_dict,idx_to_buddy_dict,2)

    # unique_users(cfg.PROCESSED_DIR_PATH)
    # common_users(cfg.PROCESSED_DIR_PATH,1)