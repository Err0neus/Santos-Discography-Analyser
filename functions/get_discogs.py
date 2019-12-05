##
#### Discogs Projects ####
# Getting data of any given artist using discogs api
    # connecting to discogs client using token
    # get artist id 
    # get artist data eg. Name, Albums, Songs, Year
    # get tracks/song from each Albums and track position
# Final result-> Dataframe
##
import requests
import lxml.html
import cssselect
import pandas as pd
import discogs_client
import requests
import time

# authenticate to DISCOGS.COM
token = 'FBvXNlFYwMjpXpOkCBYtlyNdawVggJqXcQZJLoJC'
discogs = discogs_client.Client('myApp',  user_token= token)

##
# fetch artist id using their name
# param: artist_name-> string
# return: id-> int
#
##
def getArtistID(artist_name):
    #
    artist_data = str(discogs.search(artist_name, type = 'artist')[0])
    artist_id = int(artist_data.split(' ')[1])
    artist_nam = artist_data.split("'")[1]
    return (artist_id, artist_nam)


##
#
# fetching track list form albums ID and creating a Dataframe
# param: df-> dataframe
# return: df-> dataframe
#
##
def getTrack(df):
    id_ls = dict(zip(df["ID"], df["TYPES"]))
    a_id, track_num, track_title = [], [], []
    track_info = pd.DataFrame()
    for albums_id, albums_types in id_ls.items():
        time.sleep(0.5)
        release = discogs.master(int(albums_id))
        m_release = release.tracklist
        for track in m_release:
            a_id.append(albums_id)
            track_num.append(track.position)
            track_title.append(track.title)
    track_info["ID"] = a_id
    track_info["TRACK_POSITION"] = track_num
    track_info["TRACK_TITLE"] = track_title

    return track_info

def dataCleaning(df):
    find_str = "Live|Best Of|Tour|Volume|Concert|Demo|Vol|Unplugged|Unreleased|Collection|Portrait"
    df["EXCLUDE_ALBUM"] = ((df["ALBUMS"].str.contains(find_str)) | (df.duplicated(subset=["ALBUMS"], keep='first'))).copy()
    clean_data = df[(df["ALBUMS_TYPES"] != "(Comp)") & (df["ALBUMS_TYPES"] != "(Comp, Album)")\
                      & (df["TYPES"] != "release") & ~(df["ALBUMS"].isnull()) & ~(df["ALBUMS_TYPES"].isnull())]
#     clean_data = df[(df["ALBUMS_FLAGE"] != True) & (df["ALBUMS_TYPES"] != "(Comp)") & (df["ALBUMS_TYPES"] != "(Comp, Album)")\
#                           & (df["TYPES"] != "release") & ~(df["ALBUMS"].isnull()) & ~(df["ALBUMS_TYPES"].isnull())]

    return clean_data

def extract(el, css_sel):
    ms = el.cssselect(css_sel)
    return None if len(ms) != 1 else ms[0].text

def cleaningTrackData(df, a_nam):
    data = df[(df["TRACK_TITLE"] != "")|(df["TRACK_POSITION"] != "")]# filter any empty track title
    data["ARTIST_NAME"] = (a_nam).title() # adding new column with given artist name
    
    #SONGS REPEATED WITH " ("
    for i, r in data.iterrows():
        data.loc[(data["TRACK_TITLE"].str.len() >= len(r["TRACK_TITLE"])+ 2)\
                     &(data["TRACK_TITLE"].str[:len(r["TRACK_TITLE"])+ 2]==r["TRACK_TITLE"]+" (")\
                       | (data.duplicated(subset=["TRACK_TITLE"], keep='first')),
                    "EXCLUDE_SONG"] = True
        
    data["EXCLUDE_SONG"].fillna(False, inplace = True)

    return data

##
# getting artist data [ name, albums, songs, type and year] from artist name
# 
# @parma - a_name : string -> artist name
# @retrun - dataframe 
#
##
def getArtistData(a_name):
    a_id, a_nam = getArtistID(a_name)
    url = "http://www.discogs.com/artist/" + str(a_id) + "?limit=500"
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    albums_info = pd.DataFrame()
    album_id, types, title, formats, year = [], [], [], [], []
 
    for row in root.cssselect("#artist tr"):
        section = extract(row, "td h3")
        if section is not None:
            if section == "Albums":
                continue
            if section == "Singles & EPs":
                break
 
        album_id.append(row.get("data-object-id"))
        types.append(row.get("data-object-type"))
        title.append(extract(row, ".title a"))
        formats.append(extract(row, ".title .format"))
        year.append(extract(row, "td[data-header=\"Year: \"]"))
    
    albums_info["ID"] = album_id
    albums_info['TYPES'] = types
    albums_info['ALBUMS'] = title
    albums_info['ALBUMS_TYPES'] = formats
    albums_info['YEAR'] = year
    
    #data cleaning
    update_df = dataCleaning(albums_info)
    
    #getting track for 
    track_info = getTrack(update_df)
    master_data = update_df.merge(track_info, on = "ID")
    
    final_data = cleaningTrackData(master_data, a_nam)

    return final_data[["ID", "ARTIST_NAME", "ALBUMS", "YEAR", "TRACK_TITLE", "TRACK_POSITION", "EXCLUDE_ALBUM", "EXCLUDE_SONG"]]
    
    # final_data = final_data[final_data["TRACK_TITLE"] != ""]# filter any empty track title
    # final_data["ARTIST_NAME"] = (a_nam).title()# change it to correct name---artist
    
    # #SONGS REPEATED WITH " ("
    # for i, r in final_data.iterrows():
    #     final_data.loc[(final_data["TRACK_TITLE"].str.len() >= len(r["TRACK_TITLE"])+ 2)\
    #                  &(final_data["TRACK_TITLE"].str[:len(r["TRACK_TITLE"])+ 2]==r["TRACK_TITLE"]+" (")\
    #                    | (final_data.duplicated(subset=["TRACK_TITLE"], keep='first')),
    #                 "EXCLUDE_SONG"] = True
        
    # final_data["EXCLUDE_SONG"].fillna(False, inplace = True) 
    
