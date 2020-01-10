import lyricsgenius

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

def getLyrics(df):
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

def getLyrics_V2(df):
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
    
    return filter_data