import lyricsgenius
# authenticate to GENIUS.COM
genius = lyricsgenius.Genius("yUrV_dD4VMSNbqnx4GERtNJAdeX1121T1OqR8nZMtbQI7Tsi1vrc2Hpxmgrb0l-S")
genius.verbose = False
genius.remove_section_headers = True
##

def getLyrics(df):
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)]
    atrist_name = filter_data["ARTIST_NAME"].unique()[0]
    
    for track in filter_data.TRACK_TITLE:
        song = genius.search_song(track, atrist_name)       
        if song is None: # to abort error when lyrics is not found for particular songs
            filter_data.loc[df["TRACK_TITLE"] == track, "LYRICS"] = "Not Found"
        else:
            filter_data.loc[df["TRACK_TITLE"] == track, "LYRICS"] = song.lyrics
            
    return filter_data