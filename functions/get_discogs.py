##
#### Discogs Projects ####
# Getting data of any given artist using discogs api
    # connecting to discogs client using token
    # get artist id 
    # get artist data eg. Name, Albums, Songs, Year
    # get tracks/song from each Albums and track position
# Final result-> Dataframe
##
import lxml.html
import cssselect
import pandas as pd
import discogs_client
import time
import requests
import re
from bs4 import BeautifulSoup as bs
from tqdm import tnrange, tqdm_notebook, notebook

# authenticate to DISCOGS.COM
token = 'FBvXNlFYwMjpXpOkCBYtlyNdawVggJqXcQZJLoJC'
discogs = discogs_client.Client('myApp',  user_token= token)


def get_track_genius(df):
    '''
    Getting track name from each albums for a particular atrist name using request from "https://genius.com" 
    
    @param: df-> DataFrame
    
    @return: DataFrame containing track name for every albums and genius link for a lyrics
    '''
    
    #Creating new columns -> removing any special char and replacing space by "-"
    df["new_artist"] = (df['ARTIST_NAME'].str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})).replace(" ", "-", regex = True)
    df["new_albums"] = (df['ALBUMS'].str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})).replace(" ", "-", regex = True).replace("--", "-", regex = True)
    ls_a_id, ls_type, ls_artist_name, ls_albums, ls_year, ls_album_type, ls_track, ls_genius_link = [], [], [], [], [], [], [], []
    artist_df = pd.DataFrame()
    print("Getting Track titles for each albums from Genius..")
    for i in notebook.tqdm(range(len(df))):
        page = requests.get("https://genius.com/albums/{0}/{1}".format(df["new_artist"][i], df["new_albums"][i]))
        if page.status_code == 200: # on teh page status in 200 which means True.
            html = bs(page.text, 'html.parser')
            find_class = html.findAll('div', class_= "chart_row-content") # finding all the html tag "div" where the class name is "chart_row-content"
            for tags in find_class:
                links = tags.find("a", class_= 'u-display_block')
                # appending to the emply list
                ls_a_id.append(df["ID"][i])
                ls_type.append(df["TYPES"][i])
                ls_artist_name.append(df["ARTIST_NAME"][i])
                ls_albums.append(df["ALBUMS"][i])
                ls_year.append(df["YEAR"][i])
                ls_album_type.append(df["ALBUMS_TYPES"][i])
                ls_track.append((tags.get_text())) #appending track titles
                ls_genius_link.append(links["href"]) # appending lyrics https links for each song title
        else:
            ls_a_id.append(df["ID"][i])
            ls_type.append(df["TYPES"][i])
            ls_artist_name.append(df["ARTIST_NAME"][i])
            ls_albums.append(df["ALBUMS"][i])
            ls_year.append(df["YEAR"][i])
            ls_album_type.append(df["ALBUMS_TYPES"][i])
            ls_track.append((None))
            ls_genius_link.append(None)
    
    # Creating a dataframe 
    artist_df["ID"] = ls_a_id
    artist_df["TYPES"] = ls_type
    artist_df['ARTIST_NAME'] = ls_artist_name
    artist_df['ALBUMS'] = ls_albums
    artist_df['YEAR'] = ls_year
    artist_df["ALBUMS_TYPES"] = ls_album_type
    artist_df['TRACK_TITLE'] = ls_track
    artist_df['GENIUS_LINK'] = ls_genius_link
    #Cleaning Track title
    artist_df['TRACK_TITLE'] = (artist_df['TRACK_TITLE'].replace("\n", "", regex = True).replace("Lyrics", "", regex = True)).str.strip()

    return (artist_df)

def get_track_discog(df):
    '''
    Getting track name from the dataframe using discogs API.
    
    @param: df-> Dataframe
    
    @return: Dataframe containing track name and genuis http links
    '''
    reset_df = df.reset_index(drop = True)
    ls_a_id, ls_type, ls_artist_name, ls_albums, ls_year, ls_album_type, ls_track = [], [], [], [], [], [], []
    track_info = pd.DataFrame()
    print("Getting Track..")
    for i in notebook.tqdm(range(len(reset_df))):
        album_id = reset_df["ID"][i]
        time.sleep(0.5)
        release = discogs.master(int(album_id)) # discogs API
        m_release = release.tracklist
        for track in m_release:
            #appending into the empty list
            ls_a_id.append(album_id)
            ls_type.append(reset_df["TYPES"][i])
            ls_artist_name.append(reset_df["ARTIST_NAME"][i])
            ls_albums.append(reset_df["ALBUMS"][i])
            ls_year.append(reset_df["YEAR"][i])
            ls_album_type.append(reset_df["ALBUMS_TYPES"][i])
            ls_track.append(track.title)
#             ls_genius_link.append("https://genius.com/{0}-{1}-lyrics".format())
    
    #Adding columns into empty Dataframe
    track_info["ID"] = ls_a_id
    track_info["TYPES"] = ls_type
    track_info['ARTIST_NAME'] = ls_artist_name
    track_info['ALBUMS'] = ls_albums
    track_info['YEAR'] = ls_year
    track_info["ALBUMS_TYPES"] = ls_album_type
    track_info['TRACK_TITLE'] = ls_track
    #Creating new columns to clean up any special char. 
    track_info["new_artist"] = (track_info['ARTIST_NAME'].str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})).replace(" ", "-", regex = True)
    track_info["new_track_tile"] = (track_info['TRACK_TITLE'].str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})).replace(" ", "-", regex = True).replace("--", "-", regex = True)
    track_info['GENIUS_LINK'] = "https://genius.com/" + track_info["new_artist"].str.strip()+ "-" + track_info["new_track_tile"].str.strip()+"-lyrics"
    
    return track_info[["ID", "TYPES", "ARTIST_NAME", "ALBUMS", "YEAR", "ALBUMS_TYPES", "TRACK_TITLE", "GENIUS_LINK"]]

def data_cleaning(df):
    '''
    Cleaning Discogs datafarme. Removing 
    '''
    find_str = "Live|Best Of|Tour|Volume|Concert|Demo|Vol|Unplugged|Unreleased|Collection|Portrait"
#     df["EXCLUDE_ALBUM"] = ((df["ALBUMS"].str.contains(find_str)) | (df.duplicated(subset=["ALBUMS"], keep='first'))).copy()
    df["EXCLUDE_ALBUM"] = ((df["ALBUMS"].str.contains(find_str))).copy()
    clean_data = df[(df["ALBUMS_TYPES"] != "(Comp)") & (df["ALBUMS_TYPES"] != "(Comp, Album)")\
                      & (df["TYPES"] != "release") & ~(df["ALBUMS"].isnull()) & ~(df["ALBUMS_TYPES"].isnull())]

    return clean_data



def cleaning_track_data(df):
    data = df[~df["TRACK_TITLE"].isnull()]# filter any empty track title
#     data = data[data["TRACK_POSITION"] != ""] # filter any empty track position
    data = data.reset_index(drop=True) 
    print("Cleaning Track Title...")
    #SONGS REPEATED WITH " ("
#     for i, r in notebook.tqdm(data.iterrows()):
#         data.loc[(data["TRACK_TITLE"].str.len() >= len(r["TRACK_TITLE"])+ 2)\
#                      &(data["TRACK_TITLE"].str[:len(r["TRACK_TITLE"])+ 2]==r["TRACK_TITLE"]+" (")\
#                        | (data.duplicated(subset=["TRACK_TITLE"], keep='first')),
#                     "EXCLUDE_SONG"] = True
    data.loc[data.duplicated(subset=["TRACK_TITLE"], keep='first'), "EXCLUDE_SONG"] = True    
    data["EXCLUDE_SONG"].fillna(False, inplace = True)

    return data


def getArtistID(artist_name):
    #
    artist_data = str(discogs.search(artist_name, type = 'artist')[0])
    artist_id = int(artist_data.split(' ')[1])
    artist_nam = artist_data.split("'")[1]
    return (artist_id, artist_nam)

def get_artist_albums(a_name):
    a_id, a_nam = getArtistID(a_name)
    url = "http://www.discogs.com/artist/" + str(a_id) + "?limit=500"
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    albums_info = pd.DataFrame()
    album_id, artist_name, types, title, formats, year = [], [], [], [], [], []
    section_value = 0
    print("Getting albums data for '%s'" %a_nam)
    iterate = notebook.tqdm(range(1, len(root.cssselect("#artist tr"))))
    for i in iterate:
        row = root.cssselect("#artist tr")[i]
        section = extract(row, "td h3")
        
        if section is not None:
            section_value += 1
        
        if section_value == 0:
            album_id.append(row.get("data-object-id"))
            artist_name.append(a_name)
            types.append(row.get("data-object-type"))
            title.append(extract(row, ".title a"))
            formats.append(extract(row, ".title .format"))
            year.append(extract(row, "td[data-header=\"Year: \"]"))
    
    albums_info["ID"] = album_id
    albums_info['TYPES'] = types
    albums_info["ARTIST_NAME"] = artist_name
    albums_info['ALBUMS'] = title
    albums_info['ALBUMS_TYPES'] = formats
    albums_info['YEAR'] = year
    
    return albums_info

def getArtistData(a_name):
    '''
    Get all the Artist data from Atrist name using genius and Discogs API. 
    
    @param: a_name-> String 
    
    @return: Dataframe
    '''
    artist_albums = get_artist_albums(a_name)# dicogs API
   
    genius_track = get_track_genius(artist_albums)
    # getting track for None
    
    df_genius_none = genius_track[genius_track["TRACK_TITLE"].isnull()]
    df_genius_none = data_cleaning(df_genius_none)
    discog_track = get_track_discog(df_genius_none)
    
    final_data = pd.concat([genius_track, discog_track], ignore_index = True)
    final_data = cleaning_track_data(data_cleaning(final_data))
    
    return final_data
 
