import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from os import walk
import pandas as pd
import multiprocessing


def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))

def sentiment_classify(dir_path,file_name_list):
    sid = SentimentIntensityAnalyzer()
    for file_name in file_name_list:
        if file_name.startswith("im_df"):
            df = pd.read_csv(dir_path + "/"+ file_name)
            ## Creating a new column
            df['sentiment'] = 0
            for i in range(len(df)):
                # print(df[i])
                try:
                    sentiment_value = sid.polarity_scores(df['content'][i])['compound']
                except:
                    sentiment_value = 0
                if sentiment_value > 0.05:
                    sentiment = 1
                elif sentiment_value < -0.05:
                    sentiment = -1
                else:
                    sentiment = 0
                df['sentiment'][i] = sentiment

            df.to_csv("./sentiment_personal/"+file_name)


if __name__ == "__main__":
    pd.set_option('display.max_colwidth', -1)
    dir_path = "/local/home/student/sainikhilmaram/hedgefund_data/curr_processing_dir/processed_personal/"
    # dir_path = "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/processed_personal/"
    file_names_list = []
    for (dirpath, dirnames, filnames) in walk(dir_path):
        for filename in filnames:
            file_names_list.append(filename)

    num_process = 16
    print(file_names_list)
    chunked_file_names_list = list(chunker_list(file_names_list, num_process))
    print(chunked_file_names_list)

    # sentiment_classify(file_names_list,dir_path)
    for file_names in chunked_file_names_list:
        p = multiprocessing.Process(target=sentiment_classify, args=(dir_path,file_names,))
        p.start()

