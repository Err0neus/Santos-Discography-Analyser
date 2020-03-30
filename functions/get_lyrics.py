import requests
import re
import time

from bs4 import BeautifulSoup as bs
from tqdm import tnrange, tqdm_notebook, notebook

def get_lyrics(df):
    '''
    Fetching lyric for each song using requests and Beautifulsoup libaries
    If there are any song without any lyrics then fetch from lyricsgenius api
    
    param: df-> dataframe
    
    return: dataframe with LYRICS column
    '''
    filter_data = df[(df["EXCLUDE_ALBUM"] == False) & (df["EXCLUDE_SONG"] == False)].copy(deep=True)
    filter_data = filter_data.reset_index(drop=True)

    for i in notebook.tqdm(range(len(filter_data.GENIUS_LINK))):
        page = requests.get(filter_data.GENIUS_LINK[i])
        if page.status_code == 200:
            html = bs(page.text, 'html.parser')
            find_class = html.find('div', class_='lyrics')
            
            if find_class is not None:
                lyrics = find_class.get_text()
                lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
                filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics.lstrip()
                
        else:
            filter_data.loc[filter_data["GENIUS_LINK"] == filter_data.GENIUS_LINK[i], "LYRICS"] = None
            time.sleep(3)    
    
    return (filter_data)
