#!/usr/bin/env python
# coding: utf-8

# In[2]:


# IMPORT MODULES FOR WORDCLOUD
import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt

# In[4]:


def createGroupDf(df, v_groupby, v_lyric_version):    
    df_lyric_raw_grouped = df.groupby(v_groupby)[v_lyric_version].apply(','.join).reset_index()
    #df_lyric_raw_grouped['lyrics_cleaned'] = df_lyric_raw_grouped['lyrics_cleaned'].str.replace("\r","").str.replace("\n", " ").str.split(" ")
    df_lyric_raw_grouped = df_lyric_raw_grouped.set_index(v_groupby)
    df_lyric_raw_pivot = df_lyric_raw_grouped.T #transpose to switch year to be columns
    return df_lyric_raw_pivot


# In[5]:


def grid(n):
    max_cols = 3
    if n == 2:
        return (1,2)
    elif n == 4:
        return (2,2)
    elif n == 9:
        return (3,3)
    else:
        return (max(1,int(np.ceil((n/max_cols)))),min(n,max_cols))


# In[9]:


def createWordCloud(df, col):
    data = createGroupDf(df, col, 'lyrics_cleaned')
    fig = plt.figure(figsize = (20, 15))
    col_list = data.columns
    y= grid(len(col_list))[0]
    x= grid(len(col_list))[1]
    for i in range(0, len(col_list)):
        ax = fig.add_subplot(y, x, i+1)
        plt.axis('off')
        wordcloud2 = WordCloud(max_font_size=50, max_words=75, background_color="white", stopwords=STOPWORDS)        .generate((' '.join(data[col_list[i]])))
        plt.title(col_list[i])
        plt.imshow(wordcloud2, interpolation='bilinear')

    plt.show()


