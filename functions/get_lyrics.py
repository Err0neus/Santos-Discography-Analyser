import requests
import re
import time

from bs4 import BeautifulSoup as bs
from tqdm import tnrange, tqdm_notebook

def fetch_lyrics(html_class):
    '''
    Getting Lyrics from html tag for each url
    
    @param: list of html tags
    @return: string of lyrics with line break
    '''
    ls_lyrics = []
    for web_tag in html_class:
        lyrics = web_tag.get_text(separator='<br/>')# using <br/> tag as text seprater
        ls_lyrics.append(lyrics)
    # Cleaning Lyrics
    concat_lyrics = ''.join(ls_lyrics)
    lyrics_remove1 = re.sub(r'\[.*?\]', '', concat_lyrics) # Removing any character within []
    line_break_lyrics = lyrics_remove1.replace('<br/>', '\n')
    lyrics_remove2 = list(filter(None, line_break_lyrics.split('\n'))) # Removing any white space
    lyrics_clean = "\n".join(lyrics_remove2) # adding line break with clean lyrics
    
    return lyrics_clean

def get_list_of_tag(http_request):
    '''
    Get all the list of html tag with class-> Lyrics__Container
    
    return : list of html tags
    '''
    # Regular Expression that matches the class in HTML 
    regex1 = re.compile('^Lyrics__Container.*')
    
    html = bs(http_request.text, 'html.parser')
    find_class = html.find_all('div', class_= regex1)
    
    return find_class

def getLyrics(df):
    '''
    Fetching lyric for each song using requests and Beautifulsoup libaries
    If there are any song without any lyrics then fetch from lyricsgenius api
    
    param: df-> dataframe
    
    return: dataframe with LYRICS column
    '''
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True)
    filter_data = filter_data.reset_index(drop=True)

    for i in tqdm_notebook(range(len(filter_data.GENIUS_LINK))):
        page = requests.get(filter_data.GENIUS_LINK[i]) # Getting Html Tag for each links in Genius_link column 
        if page.status_code == 200 and get_list_of_tag(page) != []: # added condition to prevent infinite loop when no lyrics
            find_class = []
            while find_class == []: # Refreshing page if the find_class is empty but status_code = 200
                page = requests.get(filter_data.GENIUS_LINK[i])
                find_class = get_list_of_tag(page)
            lyrics = fetch_lyrics(find_class)
            filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics


        else:
            filter_data.loc[filter_data["GENIUS_LINK"] == filter_data.GENIUS_LINK[i], "LYRICS"] = None # If Url not found   
    
    return filter_data
