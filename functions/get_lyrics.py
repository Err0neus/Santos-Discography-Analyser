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
    regex1 = re.compile('.*lyrics.*')
    regex2 = re.compile('.*Lyrics__Container-sc-1ynbvzw-2*')

    for i in notebook.tqdm(range(len(filter_data.GENIUS_LINK))):
        page = requests.get(filter_data.GENIUS_LINK[i]) # Getting Html Tag for each links in Genius_link column 
        if page.status_code == 200:
            html = bs(page.text, 'html.parser')
            find_class = html.find('div', class_= regex1)# Matching string for the class
            
            if find_class is not None:
                lyrics = find_class.get_text() # getting text from the given class
#                 lyrics2 = re.sub(r'\([^)]*\)', '', lyrics) #Removes any character within ()
                lyrics2 = re.sub(r"\[.*?\]", '', lyrics) #Removes any character within []
                lyrics3 = re.sub(r'.*?Lyrics\n\n\n\n', '', lyrics2) #Removes any character before Lyrics
                lyrics4 = re.sub(r' ?\[[^)]+\]', '', lyrics3) #Remove '[adfaf\nadfa\n]' where there are line break
                filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics4.lstrip()
            else:
                find_class2 = html.find('div', class_= regex2) # Something lyrics are in different class
                if find_class2 is not None:
                    lyrics = "\n".join(find_class2.strings) 
                    lyrics2 = re.sub(r"\[.*?\]", '', lyrics) # Remove any character within []
                    lyrics3 = re.sub(r"(\w)([A-Z])", r'\1\n\2', lyrics2) # Insert line break between small and capital letter 
                    lyrics4 = re.sub(r"(')([A-Z])", r'\1\n\2', lyrics3) # Insert line break between chart ' and capital letter
                    lyrics5 = re.sub(r' ?\[[^)]+\]', '', lyrics4)
                    filter_data.loc[filter_data["GENIUS_LINK"] == filter_data["GENIUS_LINK"][i], "LYRICS"] = lyrics5.lstrip()
                
        else:
            filter_data.loc[filter_data["GENIUS_LINK"] == filter_data.GENIUS_LINK[i], "LYRICS"] = None # If Url not found
            time.sleep(0.5)    
    
    return filter_data
