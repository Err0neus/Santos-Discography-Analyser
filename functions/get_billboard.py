import requests
import re
import pandas as pd

from bs4 import BeautifulSoup as bs
from functions import get_discogs
from tqdm import tnrange, tqdm_notebook, notebook


def getBillBoardPeak(artist_name):    
    artist_id, artist_nam = get_discogs.getArtistID(artist_name)
    ls_track, ls_peak, ls_date = [], [], []
    for i in range(1, 60):
        url1 = "https://www.billboard.com/music/{0}/chart-history/HSI/{1}".format(artist_nam, i)
        url2 = "https://www.billboard.com/music/{0}/chart-history".format(artist_nam)
        page1 = requests.get(url1)
        page2 = requests.get(url2)

        if page1.status_code == 200:
            html = bs(page1.text, 'html.parser')

            find_chart_his = html.findAll("div", class_= "chart-history__item")

        elif page2.status_code == 200 and i == 1: # going for one loop only 
            html = bs(page2.text, 'html.parser')

            find_chart_his = html.findAll("div", class_= "chart-history__item")

        else:
            break


        for tags in find_chart_his:
            # getting track 
            find_track = tags.find("p", class_= "chart-history__titles__list__item__title color--primary font--semi-bold")
            track = find_track.get_text()
            ls_track.append(track)

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
    df_billboard = pd.DataFrame({"TRACK_TITLE" : ls_track, "BILLBOARD_RANK" : ls_peak, "DATE" : ls_date})
    df_billboard["ARTIST_NAME"] = artist_nam
    df_billboard["DATE"] = pd.to_datetime(df_billboard["DATE"], format = "%d.%m.%Y")
    df_final_billboard = df_billboard.sort_values(by = ["DATE"]).reset_index(drop = True)
    return df_final_billboard[["ARTIST_NAME", "TRACK_TITLE", "BILLBOARD_RANK", "DATE"]]