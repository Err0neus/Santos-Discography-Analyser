##
#### Discogs Projects ####
# Getting data of any given artist using Request on discogs website
    # connecting to discogs client using token
    # get artist id 
    # get artist data eg. Name, Albums, Songs, Year
    
# Getting artist track/song for each Albums from Genius Request

# Final result-> Dataframe
##
import lxml.html
import cssselect
import pandas as pd
import discogs_client
import time
import requests
import re
import fuzzy_pandas as fpd
from bs4 import BeautifulSoup as bs
from tqdm import tqdm, tqdm_notebook

# authenticate to DISCOGS.COM
token = 'FBvXNlFYwMjpXpOkCBYtlyNdawVggJqXcQZJLoJC'
discogs = discogs_client.Client('myApp',  user_token= token)


def get_track_genius(df):
    '''
    Getting track name from each album for a particular atrist name using request from "https://genius.com" 
    
    @param: df-> DataFrame
    
    @return: DataFrame containing track name for every albums and genius link for a lyrics
    '''
    reset_df = df.reset_index(drop = True)# re indexing dataframe
    #Creating new columns -> removing any special char and replacing space by "-"
    reset_df["new_artist"] = ((reset_df['ARTIST_NAME'].str.replace("&", "and", regex = True).replace("/", " ", regex = True)
                              ).str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})
                             ).replace(" ", "-", regex = True)
    reset_df["new_albums"] = ((reset_df['ALBUMS'].str.replace(".", " ", regex = True)
                              ).str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})
                             ).replace(" ", "-", regex = True).replace("--", "-", regex = True)
    ls_a_id, ls_type, ls_artist_name, ls_albums, ls_year, ls_album_type, ls_have, ls_want, ls_rating, ls_rating_count, ls_track, ls_genius_link = [], [], [], [], [], [], [], [], [], [], [], []
    artist_df = pd.DataFrame()
    print("Getting Track titles from Genius Lyrics..")
    for i in tqdm_notebook(range(len(reset_df))):
        #creating url for genius
        page = requests.get("https://genius.com/albums/{0}/{1}".format(reset_df["new_artist"][i]
                                                                       , reset_df["new_albums"][i])
                           )
        # prcessing only the status with 200 (sucessfully connected)
        if page.status_code == 200: 
            html = bs(page.text, 'html.parser')
            find_class = html.findAll('div', class_= "chart_row-content") # finding all the html tag "div" where the class name is "chart_row-content"
            for tags in find_class:
                links = tags.find("a", class_= 'u-display_block')
                # appending to the emply list
                ls_a_id.append(reset_df["ARTIST_ID"][i])
                ls_type.append(reset_df["TYPES"][i])
                ls_artist_name.append(reset_df["ARTIST_NAME"][i])
                ls_albums.append(reset_df["ALBUMS"][i])
                ls_year.append(reset_df["YEAR"][i])
                ls_album_type.append(reset_df["ALBUMS_TYPES"][i])
                ls_have.append(reset_df["NUM_OF_PPL_HAVING"][i])
                ls_want.append(reset_df["NUM_OF_PPL_WANT"][i])
                ls_rating.append(reset_df["AVG_RATING"][i])
                ls_rating_count.append(reset_df["NUM_OF_RATING"][i])
                ls_track.append((tags.get_text())) #appending track titles
                ls_genius_link.append(links["href"]) # appending lyrics https links for each song title
        else:
            ls_a_id.append(reset_df["ARTIST_ID"][i])
            ls_type.append(reset_df["TYPES"][i])
            ls_artist_name.append(reset_df["ARTIST_NAME"][i])
            ls_albums.append(reset_df["ALBUMS"][i])
            ls_year.append(reset_df["YEAR"][i])
            ls_album_type.append(reset_df["ALBUMS_TYPES"][i])
            ls_have.append(reset_df["NUM_OF_PPL_HAVING"][i])
            ls_want.append(reset_df["NUM_OF_PPL_WANT"][i])
            ls_rating.append(reset_df["AVG_RATING"][i])
            ls_rating_count.append(reset_df["NUM_OF_RATING"][i])
            ls_track.append((None))
            ls_genius_link.append(None)
    
    # Creating a dataframe 
    artist_df["ARTIST_ID"] = ls_a_id
    artist_df["TYPES"] = ls_type
    artist_df['ARTIST_NAME'] = ls_artist_name
    artist_df['ALBUMS'] = ls_albums
    artist_df['YEAR'] = ls_year
    artist_df["ALBUMS_TYPES"] = ls_album_type
    artist_df["NUM_OF_PPL_HAVING"] = ls_have
    artist_df["NUM_OF_PPL_WANT"] = ls_want
    artist_df["AVG_RATING"] = ls_rating
    artist_df["NUM_OF_RATING"] = ls_rating_count
    artist_df['TRACK_TITLE'] = ls_track
    artist_df['GENIUS_LINK'] = ls_genius_link
    #Cleaning Track title
    artist_df['TRACK_TITLE'] = (artist_df['TRACK_TITLE'].replace("\n", "", regex = True).replace("Lyrics"
                                                                                                 , "", regex = True)
                               ).str.strip()

    return (artist_df)

def get_track_discog(df):
    '''
    Getting track name from the dataframe using discogs API.
    
    @param: df-> Dataframe
    
    @return: Dataframe containing track name and genuis http links
    '''
    reset_df = df.reset_index(drop = True)
    ls_a_id, ls_type, ls_artist_name, ls_albums, ls_year, ls_album_type, ls_have, ls_want, ls_rating, ls_rating_count, ls_track = [], [], [], [], [], [], [], [], [], [], []
    track_info = pd.DataFrame()
    print("Getting Tracks..")
    for i in tqdm_notebook(range(len(reset_df))):
        album_id = reset_df["ARTIST_ID"][i]
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
            ls_have.append(reset_df["NUM_OF_PPL_HAVING"][i])
            ls_want.append(reset_df["NUM_OF_PPL_WANT"][i])
            ls_rating.append(reset_df["AVG_RATING"][i])
            ls_rating_count.append(reset_df["NUM_OF_RATING"][i])
            ls_track.append(track.title)
#             ls_genius_link.append("https://genius.com/{0}-{1}-lyrics".format())
    #Adding columns into empty Dataframe
    track_info["ARTIST_ID"] = ls_a_id
    track_info["TYPES"] = ls_type
    track_info['ARTIST_NAME'] = ls_artist_name
    track_info['ALBUMS'] = ls_albums
    track_info['YEAR'] = ls_year
    track_info["ALBUMS_TYPES"] = ls_album_type
    track_info['TRACK_TITLE'] = ls_track
    track_info["NUM_OF_PPL_HAVING"] = ls_have
    track_info["NUM_OF_PPL_WANT"] = ls_want
    track_info["AVG_RATING"] = ls_rating
    track_info['NUM_OF_RATING'] = ls_rating_count
    #Creating new columns to clean up any special char. 
    track_info["new_artist"] = ((track_info['ARTIST_NAME'].str.replace("&", "and", regex = True
                                                                      ).replace("/", " ", regex = True)
                                ).str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})
                               ).replace(" ", "-", regex = True)
    track_info["new_track_tile"] = ((track_info['TRACK_TITLE'].str.replace("'", " ", regex = True)
                                    ).str.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+'"})
                                   ).replace(" ", "-", regex = True).replace("--", "-", regex = True)
    track_info['GENIUS_LINK'] = "https://genius.com/" + track_info["new_artist"].str.strip()+ "-" + track_info["new_track_tile"].str.strip()+"-lyrics"
    
    return track_info[["ARTIST_ID"
                       , "TYPES"
                       , "ARTIST_NAME"
                       , "ALBUMS"
                       , "YEAR"
                       , "ALBUMS_TYPES"
                       , "TRACK_TITLE"
                       , "NUM_OF_PPL_HAVING"
                       , "NUM_OF_PPL_WANT"
                       , "AVG_RATING"
                       , 'NUM_OF_RATING'
                       , "GENIUS_LINK"]]

def data_cleaning(df):
    '''
    Cleaning Discogs datafarme. Removing 
    '''
    
    clean_data = df[(df["ALBUMS_TYPES"] != "(Comp)") 
                    & (df["ALBUMS_TYPES"] != "(Comp, Album)") 
                    & (df["TYPES"] != "release") 
                    & ~(df["ALBUMS"].isnull()) 
                    & ~(df["ALBUMS_TYPES"].isnull())
                   ]

    return (clean_data.reset_index(drop = True))

def flag_exclude_album(df):
    '''
    Flag True for any "Live, concert, Demo, Recording etc" in the Album 
    '''
    
    find_str = "Live|Best Of|Tour|Volume|Concert|Demo|Vol|Unplugged|Unreleased|Collection|Portrait|Recordings"
    df["EXCLUDE_ALBUM"] = (df["ALBUMS"].str.contains(find_str)).copy()
    
    return (df)

def flag_track_title(df):
    '''
    Flag True for any duplicated track name.
    '''
    data = df[~df["TRACK_TITLE"].isnull()]# filter any empty track title
    data_sort = data.sort_values(by = ["YEAR", "ALBUMS"]).copy()
    data_sort["EXCLUDE_SONG"] = data_sort.duplicated(subset=["TRACK_TITLE"], keep='first')
    
    return data_sort


def getArtistID(artist_name):
    '''
    Getting Artist ID from discogs.
    
    @param: artist_name-> str 
    
    @return: ID-> int, Name-> str
    '''
    artist_data = str(discogs.search(artist_name, type = 'artist')[0])
    artist_id = int(artist_data.split(' ')[1])
    artist_nam = artist_data.split("'")[1]
    return (artist_id, re.sub('[\(\[]\d[\)\]]',"", artist_nam).strip())


def get_stat_link(url, df):
    '''
    Webscrapping artist page
    Getting hyperlinks for the each album
    
    @param: url-> string [http link]
    @param: df-> DataFrame
    
    @return: DataFrame [add new colum STAT_LINK]
    '''
    r_get = requests.get(url)
    html = bs(r_get.text, 'html.parser')
    find_class = html.findAll('td', class_= "title")
    
    print("Getting Albums links in Discogs..")
    # getting the links for the stat page
    for i in tqdm_notebook(range(len(find_class))):
        links = find_class[i].find("a")
        album_ids = links["href"][links["href"].rfind("/")+1:]
        df.loc[df["ARTIST_ID"] == album_ids, "STAT_LINK"] = "https://www.discogs.com" + links["href"]
    
    return df

def get_album_stat(url, df):
    '''
    webscrapping album page
    Getting AVG RATING, RATING, HAVE and WANT of the albums
    
    @param: url-> string [http link]
    @param: df-> DataFrame
    
    @return: DataFrame [add new colum RATING_VALUE, RATING_COUNT]
    '''
    df_stat_link = get_stat_link(url, df)
    # webscrapping each album website
    for idx, row in df_stat_link.iterrows():
        stat_request = requests.get(row["STAT_LINK"])
        html_tags = bs(stat_request.text, 'html.parser')
        
        avg_rating = html_tags.find("span", class_="rating_value")
        num_rating = html_tags.find("span", class_="rating_count")
        num_have = html_tags.find("a", class_="coll_num")
        num_want = html_tags.find("a", class_="want_num")
        
        if avg_rating is not None:
            df_stat_link.loc[df_stat_link["ARTIST_ID"] == row["ARTIST_ID"], "AVG_RATING"] = avg_rating.get_text()
        
        if num_rating is not None:
            df_stat_link.loc[df_stat_link["ARTIST_ID"] == row["ARTIST_ID"], "NUM_OF_RATING"] = num_rating.get_text()
        
        if num_have is not None:
            df_stat_link.loc[df_stat_link["ARTIST_ID"] == row["ARTIST_ID"], "NUM_OF_PPL_HAVING"] = num_have.get_text()
        
        if num_want is not None:
            df_stat_link.loc[df_stat_link["ARTIST_ID"] == row["ARTIST_ID"], "NUM_OF_PPL_WANT"] = num_want.get_text()
    
    return df_stat_link.drop(['STAT_LINK'], axis=1)


def extract(el, css_sel):
    ms = el.cssselect(css_sel)
    return None if len(ms) != 1 else ms[0].text

def get_artist_albums(a_name):
    '''
    Getting album details for a particular artist name
    
    @param: a_name-> str (artist name)
    
    @return: dataframe
    '''
    a_id, a_nam = getArtistID(a_name)
    url = "http://www.discogs.com/artist/" + str(a_id) + "?limit=500"
    r = requests.get(url)
    root = lxml.html.fromstring(r.text)
    albums_info = pd.DataFrame()
    album_id, artist_name, types, title, formats, year = [], [], [], [], [], []
    section_value = 0
    print("Getting albums data for '%s'" %a_nam)
    iterate = tqdm_notebook(range(1, len(root.cssselect("#artist tr"))))
    for i in iterate:
        row = root.cssselect("#artist tr")[i]
        section = extract(row, "td h3")
        
        if section is not None:
            section_value += 1
        
        if section_value == 0:
            album_id.append(row.get("data-object-id"))
            artist_name.append(a_nam)
            types.append(row.get("data-object-type"))
            title.append(extract(row, ".title a"))
            formats.append(extract(row, ".title .format"))
            year.append(extract(row, "td[data-header=\"Year: \"]"))
    
    albums_info["ARTIST_ID"] = album_id
    albums_info['TYPES'] = types
    albums_info["ARTIST_NAME"] = artist_name
    albums_info['ALBUMS'] = title
    albums_info['ALBUMS_TYPES'] = formats
    albums_info['YEAR'] = year
    # Only getting albums tiltes which are not None
    filter_albums = albums_info[~(albums_info["ALBUMS"].isnull())].copy()
    
    update_albums_info = get_album_stat(url, filter_albums)
    
    return update_albums_info

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
    df_genius_none = data_cleaning(df_genius_none) # Removing any release from albums
    
    if df_genius_none.empty == False:
        discog_track = get_track_discog(df_genius_none) # using discog API
        full_data = pd.concat([genius_track, discog_track], ignore_index = True, sort = True) # appending genius and discog data
        flag_data = flag_exclude_album(full_data) # Creating flag column for an album
        final_data = flag_track_title(flag_data) # Creating flag column for a track_title
        
    else:    
        flag_data = flag_exclude_album(genius_track) # Creating flag column for an album
        final_data = flag_track_title(flag_data) # Creating flag column for a track_title
    
    #sorting data by its years
    final_data_sort = final_data.sort_values(by = ["YEAR"]).rename(columns={"NUM_OF_PPL_HAVING" : "DISCOG_PPL_HAVING"
                                                                            , "NUM_OF_PPL_WANT" : "DISCOG_PPL_WANT"
                                                                            , "NUM_OF_RATING" : "DISCOG_RATING"
                                                                            , "AVG_RATING" : "DISCOG_AVG_RATING"
                                                                           }
                                                                  ).reset_index(drop = True)
    
    # Creating new album column & track without any brackets
    final_data_sort["CLEAN_ALBUM_COL"] = final_data_sort["ALBUMS"].str.replace(r"\s+\(.*\)","")
    final_data_sort["CLEAN_TRACK_COL"] = final_data_sort["TRACK_TITLE"].str.replace(r"\s+\(.*\)","")
    
    # Get billboard ranking for albums and tracks
    df_billboard_albums = getBillBoardPeak(a_name)
    df_billboard_tracks = getBillBoardPeak(a_name, 0)
    
    #Merge discog data with billboard data
    df_discog_album = fpd.fuzzy_merge(final_data_sort, df_billboard_albums, 
                          left_on = ['ARTIST_NAME', 'CLEAN_ALBUM_COL'], 
                          right_on = ['BILLBOARD_ARTIST_NAME', 'BILLBOARD_ALBUM'],
                          method = 'levenshtein', 
                          threshold = 0.85,
                          join = 'left-outer').drop(['BILLBOARD_ARTIST_NAME'], axis = 1)

    full_data = fpd.fuzzy_merge(df_discog_album, df_billboard_tracks, 
                          left_on = ['ARTIST_NAME', 'CLEAN_TRACK_COL'], 
                          right_on = ['BILLBOARD_ARTIST_NAME', 'BILLBOARD_TRACK_TITLE'],
                          method = 'levenshtein', 
                          threshold = 0.85,
                          join = 'left-outer')
    
    # Converting list of columns to integer
    cols = ["DISCOG_PPL_HAVING"
            , "DISCOG_PPL_WANT"
            , "DISCOG_RATING"
            , "DISCOG_AVG_RATING"
            , "BILLBOARD_ALBUM_RANK"
            , "BILLBOARD_TRACK_RANK"
           ]
    
    full_data[cols] = full_data[cols].apply(pd.to_numeric, errors='coerce')
    
    return full_data[["ARTIST_ID"
                       , "ARTIST_NAME"
                       , "ALBUMS"
                       , "YEAR"
                       , "TRACK_TITLE"
                       , "DISCOG_PPL_HAVING"
                       , "DISCOG_PPL_WANT"
                       , "DISCOG_RATING"                       
                       , "DISCOG_AVG_RATING"
                       , "EXCLUDE_ALBUM"
                       , "EXCLUDE_SONG"
                       , "GENIUS_LINK"
                       , "BILLBOARD_ALBUM_RANK"
                       , "BILLBOARD_TRACK_RANK"
                       , "BILLBOARD_TRACK_TITLE"
                      ]
                     ].sort_values(by = ["YEAR", "ARTIST_ID"]).drop_duplicates()


def getBillBoardPeak(artist_name, flag:int = 1):
    '''
    Gets Artist billboard 100 using request & beautifulSoup
    By Default gets Album
    
    @param: artist_name -> string
    @param: flag -> int 0 or 1[by default 1]
    
        flag type = 1 -> gets albums
        flag type = 0 -> gets track titles
            
    @return: Dataframe    
    '''
    #getting discogs artist name
    artist_id, artist_nam = getArtistID(artist_name)
    
    ls_al_tr, ls_peak, ls_date = [], [], []
    #TLP -> albums & HSI -> billboard 100 songs/track title
    if flag == 1:
        x = "TLP"
        
    else:
        x = "HSI"
        
    for i in range(1, 60):
        url = "https://www.billboard.com/music/{0}/chart-history/{1}/{2}".format(artist_nam, x, i)
        page = requests.get(url)

        if page.status_code == 200:
            html = bs(page.text, 'html.parser')

            find_chart_his = html.findAll("div", class_= "chart-history__item")

        else:
            break


        for tags in find_chart_his:
            # getting track 
            find_track = tags.find("p", class_= "chart-history__titles__list__item__title color--primary font--semi-bold")
            album_track = find_track.get_text()
            ls_al_tr.append(album_track)

            # getting Billborad Rank 
            find_bb_number = tags.find("p", class_ = "chart-history__titles__list__item__peak")
            number = find_bb_number.get_text()
            num = re.findall(r'#(\d+)', number)[0]
            ls_peak.append(num)

            # getting date
            find_date = tags.find("a", class_ = "color--secondary font--bold")
            date = find_date.get_text()
            ls_date.append(date)

    # Creating Dataframe
    if x == 'TLP':
        df_billboard = pd.DataFrame({"BILLBOARD_ALBUM" : ls_al_tr
                                     , "BILLBOARD_ALBUM_RANK" : ls_peak
                                     , "BILLBOARD_ALBUM_DATE" : ls_date}
                                   )
        df_billboard["BILLBOARD_ARTIST_NAME"] = artist_nam
        df_billboard["BILLBOARD_ALBUM_DATE"] = pd.to_datetime(df_billboard["BILLBOARD_ALBUM_DATE"], format = "%d.%m.%Y")
        df_billboard["BILLBOARD_ALBUM"] = df_billboard["BILLBOARD_ALBUM"].astype(str)
        df_billboard["BILLBOARD_ALBUM"] = df_billboard["BILLBOARD_ALBUM"].str.replace(r"\s+\(.*\)","")
        df_final_billboard = df_billboard.sort_values(by = ["BILLBOARD_ALBUM_DATE"]).reset_index(drop = True)
        #return datafram with album for a particular artist
        return df_final_billboard[
                                  ["BILLBOARD_ARTIST_NAME"
                                   , "BILLBOARD_ALBUM"
                                   , "BILLBOARD_ALBUM_RANK"
                                   , "BILLBOARD_ALBUM_DATE"
                                  ]
                                 ]
    
    else:
        df_billboard = pd.DataFrame({"BILLBOARD_TRACK_TITLE" : ls_al_tr
                                     , "BILLBOARD_TRACK_RANK" : ls_peak
                                     , "BILLBOARD_TRACK_DATE" : ls_date}
                                   )
        df_billboard["BILLBOARD_ARTIST_NAME"] = artist_nam
        df_billboard["BILLBOARD_TRACK_DATE"] = pd.to_datetime(df_billboard["BILLBOARD_TRACK_DATE"], format = "%d.%m.%Y")
        df_billboard["BILLBOARD_TRACK_TITLE"] = df_billboard["BILLBOARD_TRACK_TITLE"].astype(str)
        df_billboard["BILLBOARD_TRACK_TITLE"] = df_billboard["BILLBOARD_TRACK_TITLE"].str.replace(r"\s+\(.*\)","")
        df_final_billboard = df_billboard.sort_values(by = ["BILLBOARD_TRACK_DATE"]).reset_index(drop = True)
        #return dataframe with track titles for a particular artist
        return df_final_billboard[
                                  ["BILLBOARD_ARTIST_NAME"
                                   , "BILLBOARD_TRACK_TITLE"
                                   , "BILLBOARD_TRACK_RANK"
                                   , "BILLBOARD_TRACK_DATE"
                                  ]
                                 ]
