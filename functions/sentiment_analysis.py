# Imports
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
import numpy as np
import pandas as pd

from tqdm import tnrange, tqdm_notebook, notebook

# function

def sentimentAnalyser(df, artist):
    ''' adds sentiment values for all lyrics of the specified artist in the provided input '''
    sid = SentimentIntensityAnalyzer()
    i=0
    ls_percentage_negative = []
    ls_percentage_neutral = []
    ls_percentage_positive = []
    # make a list of songs of the selected artist that actually have lyrics
    song_list = df[
        (df['ARTIST_NAME']==artist) & \
        (~df['LYRICS'].isna())
    ]['TRACK_TITLE']
    for i in notebook.tqdm(range(len(song_list))):
        for song in song_list:
            # transform artist-song lyrics into a list
            lyrics_list = df[(df['ARTIST_NAME'] == artist) & \
                             (df['TRACK_TITLE'] == song)
                            ]['LYRICS'].str.split('\n').tolist()[0]
            num_negative=0
            num_neutral =0
            num_positive =0
            for sentence in lyrics_list:
                ss = sid.polarity_scores(sentence)
                comp = ss['compound']
                if comp >= 0.2:
                    num_positive += 1
                elif comp > -0.2 and comp < 0.2:
                    num_neutral += 1
                else:
                    num_negative += 1
            num_lines = num_negative+num_neutral+num_positive
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song), \
                "percentage_negative"
            ] = num_negative/num_lines*100
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song), \
                "percentage_neutral"
            ] = num_neutral/num_lines*100
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song), \
                "percentage_positive"
            ] = num_positive/num_lines*100
    
    return df
