import requests
import re
import time

from bs4 import BeautifulSoup as bs
from tqdm import tnrange, tqdm_notebook, notebook

def getLyrics(df):
    '''
    Fetching lyric for each song using requests and Beautifulsoup libaries
    If there are any song without any lyrics then fetch from lyricsgenius api
    
    param: df-> dataframe
    
    return: dataframe with LYRICS column
    '''
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True)
    filter_data = filter_data.reset_index(drop=True)
    # Regular Expression that matches the class in HTML 
    regex1 = re.compile('.*Lyrics*')

    for i in notebook.tqdm(range(len(filter_data.GENIUS_LINK))):
        page = requests.get(filter_data.GENIUS_LINK[i]) # Getting Html Tag for each links in Genius_link column 
        if page.status_code == 200:
            html = bs(page.text, 'html.parser')
            find_class = html.find('div', class_= 'lyrics')# Matching string for the class
            
            if find_class is not None:
                lyrics = find_class.get_text() # getting text from the given class
                #Cleaning Lyrics
                lyrics_remove1 = re.sub(r'\[.*?\]', '', lyrics)
                lyrics_remove2 = [re.sub("[\\[].*?[\)\]]", "", char) for char in lyrics_remove1.split("\n")]
                lyrics_remove3 = list(filter(None, lyrics_remove2))
                lyrics_clean = '\n'.join(lyrics_remove3)
                filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics_clean
            else:
                find_class2 = html.find('div', class_= regex1) # Sometime lyrics are in different class
                if find_class2 is not None:
                    #Cleaning Lyrics
                    lyrics_rm_1 = re.sub(r"(\w)([A-Z])", r'\1\n\2', find_class2.get_text()) # Insert line break between small and capital letter
                    lyrics_rm_2 = re.sub(r"(])([A-Z])", r'\1\n\2', lyrics_rm_1)# Insert line break between chart ] and capital letter
                    lyrics_rm_3 = re.sub(r"([?')])([A-Z])", r'\1\n\2', lyrics_rm_2) # Insert line break between chart ' or ? or ) and capital letter
                    lyrics_rm_4= re.sub(r'\[.*?\]', '', lyrics_rm_3) # Remove any character within []
                    lyrics_rm_5 = [re.sub("[\\[].*?[\)\]]", "", char) for char in lyrics_rm_4.split("\n")]
                    lyrics_rm_6 = list(filter(None, lyrics_rm_5))
                    lyrics_clean2 = '\n'.join(lyrics_rm_6)
                    filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics_clean2
                
        else:
            filter_data.loc[filter_data["GENIUS_LINK"] == filter_data.GENIUS_LINK[i], "LYRICS"] = None # If Url not found
            time.sleep(0.5)    
    
    return filter_data
