import lyricsgenius

from tqdm import tnrange, tqdm_notebook
#from tqdm.notebook import trange, tqdm

# authenticate to GENIUS.COM
genius = lyricsgenius.Genius("yUrV_dD4VMSNbqnx4GERtNJAdeX1121T1OqR8nZMtbQI7Tsi1vrc2Hpxmgrb0l-S")
genius.verbose = False
genius.remove_section_headers = True
##

def getLyrics(df):
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True) 
    atrist_name = filter_data["ARTIST_NAME"].unique()[0]
    
    for i in tqdm_notebook(range(len(filter_data.TRACK_TITLE))):
    #for i in tqdm(range(len(filter_data.TRACK_TITLE))):
        track = filter_data["TRACK_TITLE"][i]
        song = genius.search_song(track, atrist_name)       
        if song is None: # to abort error when lyrics is not found for particular songs
            filter_data.loc[df["TRACK_TITLE"] == track, "LYRICS"] = "Not Found"
        else:
            filter_data.loc[df["TRACK_TITLE"] == track, "LYRICS"] = song.lyrics
            
    return filter_data