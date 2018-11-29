import config as cfg
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def create_matrix(file):
    im_df = pd.read_csv(file)
    im_columns = ['sender', 'sender_buddy', 'receiver', 'receiver_buddy', 'time_stamp', 'subject', 'content']
    # unique_im_members = im_df['sender'].append(im_df['receiver']).unique().tolist()
    unique_im_buddies = im_df['sender_buddy'].append(im_df['receiver_buddy']).unique().tolist()

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
    print("Unique Buddies Count : {0}, Number of Messages : {1} ".format(unique_im_buddies_count,len(im_df.index)))
    message_matrix = np.zeros((unique_im_buddies_count,unique_im_buddies_count))
    message_adj_list = [set() for _ in range(unique_im_buddies_count)]

    for index, row in im_df.iterrows():
        sender_buddy_idx = buddy_to_idx[row['sender_buddy']]
        receiver_buddy_idx = buddy_to_idx[row['receiver_buddy']]
        message_matrix[sender_buddy_idx][receiver_buddy_idx] = message_matrix[sender_buddy_idx][receiver_buddy_idx] + 1
        message_matrix[receiver_buddy_idx][sender_buddy_idx] = message_matrix[receiver_buddy_idx][sender_buddy_idx] + 1
        message_adj_list[sender_buddy_idx].add(receiver_buddy_idx)
        message_adj_list[receiver_buddy_idx].add(sender_buddy_idx)


    ## Saving the array to text
    # np.savetxt('matrix.txt', message_matrix, delimiter=' ',fmt='%d')
    print("Highest Number of edges : {0}".format(max(map(max,message_matrix))))
    return message_matrix,message_adj_list


def create_graph(message_adj_list):
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

    # plt.axis('off')
    plt.savefig("weighted_graph.png")  # save as png
    plt.show()  # display





def construct_k_core(message_matrix,k):
    pass


def construct_kcore_networkx(message_matrix,k):

    message_matrix_non_zero_idxs = np.transpose(np.nonzero(np.triu(message_matrix, k=0)))

    G = nx.Graph()
    for idx in message_matrix_non_zero_idxs:
        row_idx = idx[0]
        col_idx = idx[1]
        # G.add_edge(row_idx,col_idx,weight=message_matrix[row_idx][col_idx])
        G.add_edge(row_idx, col_idx)


    kcore_G = nx.k_core(G,k)
    pos = nx.spring_layout(kcore_G)
    num_nodes = len(kcore_G.nodes)
    print("Number of k-core Nodes: {0}".format(num_nodes))
    colors = [1] * num_nodes
    nx.draw_networkx_nodes(kcore_G, pos, node_size=30,
                           node_color=colors, edgecolors='k',
                           cmap=plt.cm.Greys)

    nx.draw_networkx_edges(kcore_G, pos, alpha=0.5)
    plt.show()


if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    message_matrix,message_adj_list = create_matrix(cfg.PROCESSED_DIR_PATH + "im_df.csv")
    create_graph_temp(message_adj_list)
    # create_graph(message_matrix)
    # construct_kcore_networkx(message_matrix,7)