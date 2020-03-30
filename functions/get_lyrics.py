import lyricsgenius
import requests
import re

from bs4 import BeautifulSoup as bs
from tqdm import tnrange, tqdm_notebook, notebook
from lyricsmaster import LyricWiki, TorController

# pip install lyricsmaster
'''
LyricsMaster is a library for downloading lyrics from multiple lyrics providers.
The following Lyrics Providers are supported:
Lyric Wikia
AzLyrics
Genius
Lyrics007
MusixMatch
The Original Hip-Hop (Rap) Lyrics Archive - OHHLA.com
and more to come soon.
Free software: MIT license
Documentation: https://lyricsmaster.readthedocs.io.
'''

#from tqdm.notebook import trange, tqdm

# authenticate to GENIUS.COM
genius = lyricsgenius.Genius("yUrV_dD4VMSNbqnx4GERtNJAdeX1121T1OqR8nZMtbQI7Tsi1vrc2Hpxmgrb0l-S")
genius.verbose = False
genius.remove_section_headers = True
##

# from lyrics Master provider
provider = LyricWiki()

def getLyrics_v0(df):
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True) 
    atrist_name = filter_data["ARTIST_NAME"].unique()[0]
    
    for i in notebook.tqdm(range(len(filter_data.TRACK_TITLE))):
    #for i in tqdm(range(len(filter_data.TRACK_TITLE))):
        track = filter_data.reset_index(drop=True)["TRACK_TITLE"][i]
        song = genius.search_song(track, atrist_name)       
        if song is None: # to abort error when lyrics is not found for particular songs
            filter_data.loc[df["TRACK_TITLE"] == track, "LYRICS"] = "Not Found"
        else:
            filter_data.loc[df["TRACK_TITLE"] == track, "LYRICS"] = song.lyrics
            
    return filter_data

def cleanLyrics(df):
    '''
    Cleaning lyrics from the dataframe
    - Removing atrist name from the lyrics
    '''
    df["split_lyrics"] = df["LYRICS"].str.split("\n") # creating a list 
    df["rem_item"] = df["split_lyrics"].apply(lambda row: [val for val in row if ":" not in val]) # removing ":" from the list item
    df["CLEAN_LYRICS"] = df["rem_item"].str.join('\n')#.drop(["split_lyrics", "rem_item"], axis=1) # joining all str in the list

    return df.drop(["LYRICS", "split_lyrics", "rem_item", "GENIUS_LINK"], axis=1).rename(columns={"CLEAN_LYRICS" : "LYRICS"})

def getLyricsGenius(df, df2, atrist_name):
    '''
    Using Lyrics Genius api to fetch lyrics
    
    param: df-> filter dataframe
    param: df2-> master dataframe
    param: atrist_name-> name of particular atrist "String"
    
    return: datafarme with "LYRICS" column
    '''
    print("Fetching lyrics from LyricsGenius...")
    
    for i in notebook.tqdm(range(len(df.TRACK_TITLE))):
        track = df.reset_index(drop=True)["TRACK_TITLE"][i]
        song = genius.search_song(track, atrist_name)       
        if song is None: # to abort error when lyrics is not found for particular songs
            df2.loc[df2["TRACK_TITLE"] == track, "LYRICS"] = "Not Found"
        else:
            df2.loc[df2["TRACK_TITLE"] == track, "LYRICS"] = song.lyrics
            
    return df2


def getLyrics_v1(df):
    '''
    Fetching lyric for each song using lyricsmaster api
    If there are any song without any lyrics then fetch from lyricsgenius api
    
    param: df-> dataframe
    
    return: dataframe with LYRICS column
    '''
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True)
    filter_data = filter_data.reset_index(drop=True)
    atrist_name = filter_data["ARTIST_NAME"].unique()[0]
  
    for i in notebook.tqdm(range(len(filter_data.TRACK_TITLE))):
        albums = filter_data["ALBUMS"][i]
        track = filter_data["TRACK_TITLE"][i]
        fetch_lyric = provider.get_lyrics(atrist_name, album = albums, song = track)
        for album in fetch_lyric:
            for i_song in album:
                filter_data.loc[filter_data["TRACK_TITLE"] == track, "LYRICS"] = i_song.lyrics

    if filter_data["LYRICS"].isnull:
        data = filter_data[filter_data["LYRICS"].isnull()]
        final_data = getLyricsGenius(data, filter_data, atrist_name)
   
    else:
        final_data = filter_data
        
    clean_data = cleanLyrics(final_data)
    
    return (clean_data)

def getLyrics(df):
    '''
    Fetching lyric for each song using requests and Beautifulsoup libaries
    If there are any song without any lyrics then fetch from lyricsgenius api
    
    param: df-> dataframe
    
    return: dataframe with LYRICS column
    '''
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True)
    filter_data = filter_data.reset_index(drop=True)
    filter_data["GENIUS_LINK"] = ("https://genius.com/" + filter_data["ARTIST_NAME"] +" "+ filter_data["TRACK_TITLE"] + "-lyrics").replace(" ","-", regex=True)
    atrist_name = filter_data["ARTIST_NAME"].unique()[0]

    for i in notebook.tqdm(range(len(filter_data.GENIUS_LINK))):
        page = requests.get(filter_data.GENIUS_LINK[i])
        if page.status_code == 200:
            html = bs(page.text, 'html.parser')
            lyrics = html.find('div', class_='lyrics').get_text()
            if find_class is not None:
                lyrics = find_class.get_text()
                lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
                filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics            

        else:
            filter_data.loc[filter_data["GENIUS_LINK"] == filter_data.GENIUS_LINK[i], "LYRICS"] = None
            sleep(3)
  
    # getting lyric for any null data
#     if filter_data["LYRICS"].isnull:
#         data = filter_data[filter_data["LYRICS"].isnull()]
#         final_data = getLyricsGenius(data, filter_data, atrist_name)
   
#     else:
#         final_data = filter_data
        
    clean_data = cleanLyrics(final_data)
    
    return (clean_data)
