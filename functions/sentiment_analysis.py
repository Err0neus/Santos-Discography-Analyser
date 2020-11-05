# Imports
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
import numpy as np
import pandas as pd

from tqdm import tnrange, tqdm_notebook

# function
# Imports
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
import numpy as np
import pandas as pd

from tqdm import tnrange, tqdm_notebook

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
    ]['TRACK_TITLE'].reset_index(drop=True)
    if len(song_list) == 0:
        df["SENTIMENT_PCT_NEGATIVE"] = np.nan
        df["SENTIMENT_PCT_NEUTRAL"] = np.nan
        df["SENTIMENT_PCT_POSITIVE"] = np.nan
        df["SENTIMENT_COMPOUND_SCORE"] = np.nan
#         df["SENTIMENT_GROUP"] = np.nan
    
    else:        
        for i in tqdm_notebook(range(len(song_list))):
            # transform artist-song lyrics into a list
            lyrics_list = df[(df['ARTIST_NAME'] == artist) & \
                             (df['TRACK_TITLE'] == song_list[i])
                            ]['LYRICS'].str.split('\n').tolist()[0]
            num_negative=0
            num_neutral =0
            num_positive =0
            compound = 0
            for sentence in lyrics_list:
                ss = sid.polarity_scores(sentence)
                comp = ss['compound']
                compound += comp
                if comp >= 0.2:
                    num_positive += 1
                elif comp > -0.2 and comp < 0.2:
                    num_neutral += 1
                else:
                    num_negative += 1
            num_lines = num_negative+num_neutral+num_positive
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song_list[i]), \
                "SENTIMENT_PCT_NEGATIVE"
            ] = num_negative/num_lines*100
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song_list[i]), \
                "SENTIMENT_PCT_NEUTRAL"
            ] = num_neutral/num_lines*100
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song_list[i]), \
                "SENTIMENT_PCT_POSITIVE"
            ] = num_positive/num_lines*100
            df.loc[
                (df['ARTIST_NAME'] == artist) & \
                (df['TRACK_TITLE'] == song_list[i]), \
                "SENTIMENT_COMPOUND_SCORE"
            ] = compound/num_lines
    df["SENTIMENT_GROUP"] = df['SENTIMENT_COMPOUND_SCORE'].apply(lambda x: 'Negative' if x <=-0.03 else ('Positive' if x >=0.03 else 'Neutral'))
    return df

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
    if len(song_list) == 0:
        df["SENTIMENT_PCT_NEGATIVE"] = np.nan
        df["SENTIMENT_PCT_NEUTRAL"] = np.nan
        df["SENTIMENT_PCT_POSITIVE"] = np.nan
        df["SENTIMENT_COMPOUND_SCORE"] = np.nan
#         df["SENTIMENT_GROUP"] = np.nan
    
    else:        
        for i in tqdm_notebook(range(len(song_list))):
            for song in song_list:
                # transform artist-song lyrics into a list
                lyrics_list = df[(df['ARTIST_NAME'] == artist) & \
                                 (df['TRACK_TITLE'] == song)
                                ]['LYRICS'].str.split('\n').tolist()[0]
                num_negative=0
                num_neutral =0
                num_positive =0
                compound = 0
                for sentence in lyrics_list:
                    ss = sid.polarity_scores(sentence)
                    comp = ss['compound']
                    compound += comp
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
                    "SENTIMENT_PCT_NEGATIVE"
                ] = num_negative/num_lines*100
                df.loc[
                    (df['ARTIST_NAME'] == artist) & \
                    (df['TRACK_TITLE'] == song), \
                    "SENTIMENT_PCT_NEUTRAL"
                ] = num_neutral/num_lines*100
                df.loc[
                    (df['ARTIST_NAME'] == artist) & \
                    (df['TRACK_TITLE'] == song), \
                    "SENTIMENT_PCT_POSITIVE"
                ] = num_positive/num_lines*100
                df.loc[
                    (df['ARTIST_NAME'] == artist) & \
                    (df['TRACK_TITLE'] == song), \
                    "SENTIMENT_COMPOUND_SCORE"
                ] = compound/num_lines
    df["SENTIMENT_GROUP"] = df['SENTIMENT_COMPOUND_SCORE'].apply(lambda x: 'Negative' if x <=-0.03 else ('Positive' if x >=0.03 else 'Neutral'))
    return df