import config as cfg
import pandas as pd
from os import walk

def unique_users(directory):
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
    return total_df

def common_users(directory):
    total_df = pd.DataFrame()
    for (dirpath, dirnames, filenames) in walk(directory):
        for filename in filenames:
            if (filename.startswith("im_df")):
                df = pd.read_csv(dirpath + '/' + filename)
                total_df = total_df.append(df, ignore_index=True)

    total_df_grouped = total_df.groupby('time_stamp')
    group1_df = total_df_grouped.get_group('02-22-07')
    group2_df = total_df_grouped.get_group('02-23-07')

    group1_buddies_unique = group1_df['sender_buddy'].append(group1_df['receiver_buddy']).unique().tolist()
    group2_buddies_unique = group2_df['sender_buddy'].append(group2_df['receiver_buddy']).unique().tolist()

    common_buddies = set(group1_buddies_unique).intersection(set(group2_buddies_unique))

    print("Group1 Unique Buddies : {0} , Group2 Unique Buddies : {1} , Common Buddies : {2}".
          format(len(group1_buddies_unique),len(group2_buddies_unique),len(common_buddies)))



if __name__ == "__main__":
    # unique_users(cfg.PROCESSED_DIR_PATH)
    common_users(cfg.PROCESSED_DIR_PATH)
