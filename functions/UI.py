print('Loading...')

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from IPython.display import clear_output, display, IFrame
from chord import Chord 
# UI
import ipywidgets as widgets
from tqdm import tnrange, tqdm_notebook

# other fuctions
from functions import get_discogs
from functions import get_lyrics
from functions import plot_wordcloud
from functions import sentiment_analysis
from functions import advanced_analytics

# word processing
import re
import os
import string
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = stopwords.words('english')
clear_output()

#-------------------------------------------------------------------------------
# GLOBAL VARIABLES

# default selected tab in the UI
selected_section = 0
selection_tab_of_section_1 = 0
selection_tab_of_section_2 = 0
selection_tab_of_section_3 = 0
selection_tab_of_section_4 = 0

# global var for discog
discog = ''
discog_store = []

#global var for artist
artist = ''



#-------------------------------------------------------------------------------
# UI SECTION 1 variables and functions
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# SECTION 1 | TAB 1 variables and functions

#global widget to type artist name
artist_input = widgets.Text()

# define function to overwrite artist from user input
def set_artist(x):
    global artist
    artist = x


# function to adapt long texts for display in charts

def adapt_title(text):
    adapted_text = []
    while len(text) > 0:
        text_slice = text[:21]
        last_char = 0 if text_slice == text else min(text_slice[::-1].find(' '), len(text_slice))
        adapted_text.append(text_slice[:None if last_char == 0 else -last_char])
        text = text[21 - last_char:]
    return '\n'.join(adapted_text)

    
    
# function to run at click of the button    
def get_discography(x):
    #clear previous output and print message
    clear_output()
    print("Looking for best match for '" + str(artist_input.value) +"'")
    time.sleep(2)
    # if already exists, load data from discog_store.csv
    global discog_store
    try:
        discog_store = pd.read_csv('discog_store.csv')
    except:
        pass       
    # try overwrite artist with artist found as best match from DISCOGS
    global artist 
    try:
        set_artist(
            get_discogs.getArtistID(artist_input.value)[1]
        )
    # if no match found from discogs, stop and print a message
    except:
        display(
            widgets.HTML(value=f'''<b><font color="red">No match found,\
        please try again </b>''',
                           layout=widgets.Layout(width="100%"))
        )
        #print(widgets"No match found, please try again")
        return UI()
    # if match found, print the corrected artist name
    print("Retrieving discography for '" + artist + "'")    
    time.sleep(1)
    # get discogs - check if in csv, else use DISCOGS API
    global discog
    if len(discog_store) == 0:
        discog = get_discogs.getArtistData(artist)
    elif artist in discog_store['ARTIST_NAME'].unique():
        discog = discog_store[discog_store['ARTIST_NAME'] == artist].copy()
    else:
        discog = get_discogs.getArtistData(artist)
#-------------------------------------------------------------------------------        
    discog['YEAR_ALBUM'] = "[" + discog['YEAR'].astype(str) + "] " \
                            + discog['ALBUMS']
    # make version for displaying in charts (with line breaks)
    discog['YEAR_ALBUM_DISPLAY'] = discog['YEAR_ALBUM'].astype(str).apply(adapt_title)
    # clear previous output
    clear_output()
    # set selected section
    global selected_section
    selected_section = 0
    # set selected  tab
    global selection_tab_of_section_1
    selection_tab_of_section_1 = 1
    # set album selecor content
    # overwrite album_filter with current selection
    global album_filter    
    set_album_filter(
        discog[discog['EXCLUDE_ALBUM'] != True]['YEAR_ALBUM'].unique().tolist()
    )         
    global album_selector     
    set_album_selector(
        discog['YEAR_ALBUM'].unique().tolist(), 
        album_filter
    )
    # display UI
    UI()
    
#-------------------------------------------------------------------------------
# SECTION 1 | TAB 2 variables and functions

#create album_filter
album_filter = []

# func to set album filter
def set_album_filter(x):
    global album_filter
    album_filter = x

discog_filtered = []

options = []
def multi_checkbox_widget(albums, albums_filter):
    options_dict = {album: widgets.Checkbox(description=album, 
                                            value=False,
                                            layout={'margin' : '-2px', 
                                                    'width' : 'initial'}) 
                    for album in albums}
    options = [options_dict[album] for album in albums]
    for option in options:
        if option.description in albums_filter:
            option.value = True
    options_widget = widgets.VBox(options, layout={'overflow': 'scroll', 
                                                   'max_height': '300px', 
                                                   'width' : 'initial'})
    multi_select = widgets.VBox([options_widget], 
                                layout=widgets.Layout(padding = "20px"))
    return multi_select

def set_album_selector(options, options_filter):
    global album_selector
    album_selector = multi_checkbox_widget(options,options_filter) 

album_selector = multi_checkbox_widget([],[])
import time

def select_deselect_all(x):
    #clear previous output
    clear_output() 
    global album_selector 
    if album_selector.children[0].children[0].value == True:
        set_album_selector(discog['YEAR_ALBUM'].unique().tolist(), [])
    else:
        set_album_selector(discog['YEAR_ALBUM'].unique().tolist(), 
                           discog['YEAR_ALBUM'].unique().tolist())
    # select this tab    
    global selected_section
    selected_section = 0
    # select sub tab
    global selection_tab_of_section_1
    selection_tab_of_section_1 = 1
    
    # display UI
    UI()
    
def apply_selection(x):
    global discog
    global discog_store

    
    #apply user selections, overwrite album_filter with current selection
    global album_selector 
    global album_filter 
    selected = []
    # read user input
    for album in album_selector.children[0].children:
        # overwrite EXCLUDE_ALBUM flag
        discog.loc[discog['YEAR_ALBUM'] == album.description, 
                   'EXCLUDE_ALBUM'] = not album.value
        #make a list of selected albums
        if album.value == True:
            selected.append(album.description)
    # set filter = list of selected albums
    set_album_filter(selected)
    # reset selector to keep the actual selections
    set_album_selector(discog['YEAR_ALBUM'].unique().tolist(), selected)
    
    #filter dataset
    global discog_filtered
    discog_filtered = discog[discog['YEAR_ALBUM'].isin(album_filter)].copy()
    #clear previous output
    clear_output() 
    
    # overwrite .CSV and update flags
    if len(discog_store) == 0:
        discog_store = discog.copy(deep=True)
    else:
        if artist not in discog_store['ARTIST_NAME'].unique():
            discog_store = discog_store.append(discog, 
                                               ignore_index=True, 
                                               sort=False)
        else:
            discog_store = discog_store[
                discog_store['ARTIST_NAME'] != artist
            ].append(discog, ignore_index=True, sort=False)
    
    try:
        discog_store.to_csv('discog_store.csv', index = False)
    except PermissionError:
        clear_output()
        display(widgets.HTML(value=f'''<b><font color="red">Permission denied: \
        make sure 'discog_store.csv' is closed and try again </b>''',
                           layout=widgets.Layout(width="100%")))
        return UI()
           
    #get lyrics
    print('Getting the lyrics, please hold on')
    # if there are any albums and songs to be included
    if len(discog_store[(discog_store['ARTIST_NAME'] == artist)
                    & (discog_store["EXCLUDE_ALBUM"] == False) 
                    & (discog_store["EXCLUDE_SONG"] == False)]) > 0:
        # and LYRICS colum does not exist yet
        if "LYRICS" not in discog_store.columns:
            # get lyrics for all records of the artist (flags considered)
            lyrics_data = get_lyrics.getLyrics(
                discog_store[discog_store['ARTIST_NAME'] == artist])
        # otherwise if there are any lyrics in current selection that are empty
        elif len(discog_store[(discog_store['ARTIST_NAME'] == artist)
                              & (discog_store["EXCLUDE_ALBUM"] == False)
                              & (discog_store["EXCLUDE_SONG"] == False)
                              &(~discog_store['LYRICS'].notnull())]) > 0:
            # look only for lyrics that have not yet been collected
            lyrics_data = get_lyrics.getLyrics(
                discog_store[(discog_store['ARTIST_NAME'] == artist) \
                             &(~discog_store['LYRICS'].notnull())])
        else:
            lyrics_data = []
    else:
        lyrics_data = []
    
    # if any new lyrics were retrieved
    if len(lyrics_data) != 0:
        # do sentiment analysis
        print('Analyzing lyrics sentiment...')
        sentiment_data = sentiment_analysis.sentimentAnalyser(
            lyrics_data, artist
        )
        
        print('processing and cleaning, please hold on')
        # iterate through results and populate the columns in main discog store
        # add lyrics
        for i,r in lyrics_data.iterrows():
            discog_store.loc[(discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                             (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']), 
                             "LYRICS"] = r['LYRICS']
        # add sentiment data
        for i,r in sentiment_data.iterrows():
            discog_store.loc[
                (discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']),
                "SENTIMENT_PCT_NEGATIVE"] = r['SENTIMENT_PCT_NEGATIVE']  
            discog_store.loc[
                (discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']),
                "SENTIMENT_PCT_NEUTRAL"] = r['SENTIMENT_PCT_NEUTRAL']
            discog_store.loc[
                (discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']),
                "SENTIMENT_PCT_POSITIVE"] = r['SENTIMENT_PCT_POSITIVE'] 
            discog_store.loc[
                (discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']),
                "SENTIMENT_COMPOUND_SCORE"] = r['SENTIMENT_COMPOUND_SCORE']            
            

        # add column with lyrics with removed stopwords
        discog_store["LYRICS_CLEAN"] = discog_store['LYRICS'].astype(str).apply(
            lambda x: ' '.join(list(word for word in re.findall(
                r"[\w]+|[^\s\w]",x.lower()
            ) if word not in stop_words
                                   )))       
        # remove punctuation
        discog_store["LYRICS_CLEAN"] = discog_store[
            'LYRICS_CLEAN'
        ].str.replace('[^\w\s] ','')
            
        #list unique clean words
        discog_store["LYRICS_CLEAN_UNIQUE"] = discog_store[
            'LYRICS_CLEAN'
        ].astype(str).apply(lambda x: list(set(x.split())))
        #count unique clean words
        discog_store["LYRICS_CLEAN_UNIQUE_COUNT"] = discog_store[
            'LYRICS_CLEAN_UNIQUE'
        ].apply(lambda x: len(x))
#-------------------------------------------------------------------------------            
    
    # write the updated content
    try:
        discog_store.to_csv('discog_store.csv', index = False)
    except PermissionError:
        clear_output()
        display(widgets.HTML(value=f'''<b><font color="red">Permission denied: \
        make sure 'discog_store.csv' is closed and try again </b>''',
                           layout=widgets.Layout(width="100%")))
        return UI()
        
    
    clear_output()
    # select tab
    global selected_section
    selected_section = 0
    # select sub tab
    global selection_tab_of_section_1
    selection_tab_of_section_1 = 2
    
    # display UI
    UI()    

#-------------------------------------------------------------------------------
# SECTION 1 | TAB 3 variables and functions

# set bin_size var with default 10
bin_size = 10

#defining a slider for bin_size selector
period_selection_slider = widgets.IntSlider(
        value=bin_size,
        min=1,
        max=10,
        step=1,
        description='Period Size (# of years)',
        style = {'description_width': 'initial'},
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='d'
    )

# define function to overwrite bin_size from slider input
def set_bin_size(x):
    global bin_size
    bin_size = period_selection_slider.value
    #clear previous output
    clear_output()
    # select next section    
    global selected_section
    selected_section = 1
    # select tab
    global selection_tab_of_section_2
    selection_tab_of_section_2 = 0
    # restart UI
    UI()
    
#-------------------------------------------------------------------------------
# UI SECTION 2 variables and functions
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# SECTION 2 | TAB 1 variables and functions

def generate_period_bins(discog, bin_size):
    '''returns list of period bins starting 0th year of the decade 
    of first release'''
    bins = []
    if bin_size == 1:
        start_year = int(discog['YEAR'].min())
        last_year = int(discog['YEAR'].max())
        year = start_year
        while year <= last_year:
            bins.append(str(year))
            year += bin_size
    else:        
        start_year = int(str(discog['YEAR'].min())[:3]+'0')
        last_year = int(discog['YEAR'].max()) \
                    + int(str(100 - int(str(discog['YEAR'].max())[2:]))[-1])
        year = start_year
        while year <= last_year:
            bins.append(str(year) + '-' + str(year + bin_size-1))
            year += bin_size
    return bins

def unique_per_period(discog, column, bin_size):
    '''returns a dataframe with count of unique values within a column 
    by defined bin size'''
    data = {'period' : generate_period_bins(discog, bin_size),
            column : []}
    if bin_size == 1:
        for period in data['period']:
            data[column].append(len(discog[discog['YEAR'] == period][column].unique()))
    else:
        for period in data['period']:
            data[column].append(
                len(
                    discog[
                        (discog['YEAR'].astype(int) >= int(period[:4])) \
                        & (discog['YEAR'].astype(int) <= int(period[5:]))
                    ][column].unique()))     
        # filter out all but one period empty before first and after last record
    output = pd.DataFrame.from_dict(data)
    # flag record with and without data
    output.loc[output[column] == 0, 'data_flag'] = 0
    output.loc[output[column] > 0, 'data_flag'] = 1
    # chronological counter
    counter1=[]
    counter = 0
    for i in range(output.shape[0]):
        if i == output.shape[0]-1:
            counter = counter + output.iloc[i]['data_flag']
            counter1.append(counter)
        elif i == 0:
            counter = counter \
                      + output.iloc[i]['data_flag'] \
                      + output.iloc[i+1]['data_flag']
            counter1.append(counter)            
        else:
            counter = counter + output.iloc[i+1]['data_flag']
            counter1.append(counter)
        output['counter1'] = pd.Series(counter1)
    # reverse - anti chronological counter
    output = output.iloc[::-1].reset_index(drop=True)
    counter2=[]
    counter = 0  
    for i in range(output.shape[0]):
        if i == output.shape[0]-1:
            counter = counter + output.iloc[i]['data_flag']
            counter2.append(counter)
        elif i == 0:
            counter = counter \
                      + output.iloc[i]['data_flag'] \
                      + output.iloc[i+1]['data_flag']
            counter2.append(counter)            
        else:
            counter = counter + output.iloc[i+1]['data_flag']
            counter2.append(counter)
        output['counter2'] = pd.Series(counter2)
    # reverse back
    output = output.iloc[::-1].reset_index(drop=True)
    # return filtered data
    return output[(output.counter1 > 0) & (output.counter2 > 0)]


def album_song_count_per_period(discog, bin_size):
    '''returns a merged dataframe by period 
    with counts of albums and songs per period'''
    data_albums = unique_per_period(discog, 'ALBUMS', bin_size)
    data_songs = unique_per_period(discog, 'TRACK_TITLE', bin_size)
    return data_albums.merge(data_songs, on = 'period')

def add_period_column(discog, bin_size):
    '''adds column with period info without any other modifications'''
    period_col_data = []
    bins = generate_period_bins(discog, bin_size)
    if bin_size == 1:
        for i, r in discog.iterrows():
            period_col_data.append(r['YEAR'])
    else:
        for i, r in discog.iterrows():
            for period in bins:
                if int(r['YEAR']) >= int(period[:4]) \
                and int(r['YEAR']) <= int(period[5:]):
                    period_col_data.append(period)
    discog['period'] = period_col_data
    return discog
                                                               
# def plot_albums_songs_per_period(discog, bin_size):
#     '''plots the number of albums and songs per period'''
    
#     data = album_song_count_per_period(discog, bin_size)
    
#     fig, ax1 = plt.subplots(figsize=(8,5))

#     color = 'tab:red'
#     ax1.set_xlabel('Year' if bin_size == 1 else str(bin_size) + '-year period')
#     ax1.set_ylabel('number of albums', color=color)

#     ax1.plot(data['period'], data['ALBUMS'], color=color)
#     ax1.tick_params(axis='y', labelcolor=color)
#     ax1.tick_params(axis='x', labelrotation=45 if len(data.index) > 5 else 0)
    
#     ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

#     color = 'tab:blue'
#     ax2.set_ylabel('number of songs', color=color)  # x-label handled with ax1
#     ax2.plot(data.index.tolist(), data['TRACK_TITLE'], color=color)
#     ax2.tick_params(axis='y', labelcolor=color)

#     fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    
#     ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
#     ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
#     ax1.set_ylim(bottom=0)
#     ax2.set_ylim(bottom=0)
#     plt.title('Albums and songs count by period', fontsize=18)
#     plt.show()

def plot_albums_songs_per_period_bar(discog, bin_size):
    '''plots the number of albums and songs per period'''
    
    width = 0.2
    #print(discog)    
    data = album_song_count_per_period(discog, bin_size).set_index('period')
    fig, ax1 = plt.subplots(figsize=(8,5))

    color = 'tab:red'


    ax1.set_ylabel('number of albums', color=color)
    #ax1.plot(data.period, data.album, color=color)
    data['ALBUMS'].plot(kind='bar', 
                        color='red', 
                        ax=ax1, 
                        width=width, 
                        position=1
                       )
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45 if len(data.index) > 5 else 0)
    ax1.set_xlabel('Year' if bin_size == 1 else str(bin_size) + '-year period')
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('number of songs', color=color)  # x-label handled with ax1
    #ax2.plot(data.index.tolist(), data.track_title, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    data['TRACK_TITLE'].plot(kind='bar', 
                             color='blue', 
                             ax=ax2, 
                             width=width, 
                             position=0)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    plt.title('Albums and songs count by period', fontsize=18)
    plt.show()
    
# def pirate_plot(discog, bin_size):
#     data = add_period_column(discog, bin_size)
#     sns.set_style("whitegrid")
#     fig, ax = plt.subplots(figsize=(8,5))
#     ax = sns.boxplot(x="period", 
#                      y="LYRICS_CLEAN_UNIQUE_COUNT", 
#                      data=data)
#     ax = sns.stripplot(x="period", 
#                        y="LYRICS_CLEAN_UNIQUE_COUNT", 
#                        data=data, 
#                        color=".25")
#     ax.set_xlabel('Period')
#     ax.set_ylabel('Number of unique words (excl. stopwords)')
#     plt.title('Lexical diversity', fontsize=18)
#     plt.show()





# function to run at click of the button_3
def show_basic_charts(x):
    global bin_size
    #clear previous output
    clear_output()
    # select current tab    
    global selected_section
    selected_section = 1
    # select sub tab
    global selection_tab_of_section_2
    selection_tab_of_section_2 = 0
    
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    discog_filtered = discog_store[
        (discog_store['ARTIST_NAME']==artist)\
        &(discog_store['YEAR_ALBUM'].isin(album_filter))
    ].copy()
    #display chart using the bin_size
    #plot_albums_songs_per_period(discog_filtered, bin_size)
    plot_albums_songs_per_period_bar(discog_filtered, bin_size)
    

#-------------------------------------------------------------------------------
# SECTION 2 | TAB 2 variables and functions

def violin_plot(discog, bin_size):
    data = add_period_column(discog, bin_size)
    # Draw Plot
    plt.figure(figsize=(8,5), dpi= 80)
    violinplot = sns.violinplot(x='period', 
                   y='LYRICS_CLEAN_UNIQUE_COUNT', 
                   data=data, 
                   scale='width', 
                   inner='quartile', 
                   cut=0)
    # rotate x axis labels
    if len(data['period'].unique()) > 5:
        for item in violinplot.get_xticklabels():
            item.set_rotation(45)
    # Decoration
    plt.title('Lexical diversity', fontsize=18)
    plt.ylabel('Number of unique words (excl. stopwords)')
    plt.xlabel('Year' if bin_size == 1 else str(bin_size) + '-year period')
    plt.show()
    
def show_lexical_diversity(x):
    global bin_size
    #clear previous output
    clear_output()
    # select current tab    
    global selected_section
    selected_section = 1
    # select sub tab
    global selection_tab_of_section_2
    selection_tab_of_section_2 = 1
    
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    discog_filtered = discog_store[
        (discog_store['ARTIST_NAME']==artist)\
        &(discog_store['YEAR_ALBUM'].isin(album_filter))
    ].copy()
    #display chart using the bin_size
    #pirate_plot(discog_filtered, bin_size)
    violin_plot(discog_filtered, bin_size)

    
    
#-------------------------------------------------------------------------------
# SECTION 2 | TAB 3 variables and functions

# function to run at click of the button_show_wordclouds
def show_wordclouds(x):
    #clear previous output
    clear_output()
    print("WordClouds are rolling in...")
    global bin_size
    # select current tab    
    global selected_section
    selected_section = 1
    # select sub tab
    global selection_tab_of_section_2
    selection_tab_of_section_2 = 2
    
    #filter dataset
    global discog_filtered
    discog_filtered = discog_store[
        (discog_store['ARTIST_NAME']==artist)\
        &(discog_store['YEAR_ALBUM'].isin(album_filter))].copy()
    
    data = add_period_column(discog_filtered, bin_size)
    
    clear_output()
    # display UI
    UI()
    if wordcloud_by_selection_dropdown.value == 'period':
        plot_wordcloud.createWordCloud(
            data[~data['LYRICS_CLEAN'].isnull()], 'period'
        )
    elif wordcloud_by_selection_dropdown.value ==  'album':
        plot_wordcloud.createWordCloud(
            data[~data['LYRICS_CLEAN'].isnull()], 'YEAR_ALBUM'
        )
    

wordcloud_by_selection_dropdown = widgets.Dropdown(options=['period', 'album',],
                                                   value='period',
                                                   description='Display by:',
                                                   disabled=False,)  





#-------------------------------------------------------------------------------
# UI SECTION 3 variables and functions
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# SECTION 3 | TAB 1 variables and functions

        
def plot_albums_discogs_popularity(discog):
    '''plots Discogs registered owners and average ratings'''
    width = 0.2
    data = pd.pivot_table(discog, 
                          index = 'YEAR_ALBUM_DISPLAY', 
                          values = ['DISCOG_PPL_HAVING', 'DISCOG_AVG_RATING'],
                          aggfunc = 'max')
    
    fig, ax1 = plt.subplots(figsize=(max(8,min(15,len(data)+2)),5))

    color = 'y'

    ax1.set_ylabel('Discogs owners', color=color)
    #ax1.plot(data.period, data.album, color=color)
    data['DISCOG_PPL_HAVING'].plot(kind='bar', 
                                   color=color, 
                                   ax=ax1, 
                                   width=width, 
                                   position=1)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.set_xlabel('Year/Album')
    xlabels = data.index.tolist()
    ax1.set_xticklabels(xlabels, ha='right')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'g'
    ax2.set_ylabel('Discogs average rating', color=color)  
    #ax2.plot(data.index.tolist(), data.track_title, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    data['DISCOG_AVG_RATING'].plot(kind='bar', 
                                   color=color, 
                                   ax=ax2, 
                                   width=width, 
                                   position=0)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    #ax1.xticks(ha='right')
    plt.title('Discogs users - owners and average ratings', fontsize=18)
    plt.show()
    
def plot_albums_ratings(discog):
    threshold = discog['DISCOG_AVG_RATING'].mean()
    data = pd.pivot_table(discog,index='YEAR_ALBUM_DISPLAY',
                          values=['DISCOG_AVG_RATING'],
                          aggfunc = 'max')
    values = np.array(data['DISCOG_AVG_RATING'].tolist())

    # plot it
    fig, ax = plt.subplots(figsize=(max(8,min(15,len(data)+2)),5))

    data['DISCOG_AVG_RATING'].plot(kind='bar', 
                                   color='y', 
                                   ax=ax, 
                                   width=0.5, 
                                   position=1)
    ax.set_ylabel('Avg. Discogs user rating')
    ax.set_xlabel('Year/Album')

    ax.tick_params(axis='x', labelrotation=45)
    xlabels = data.index.tolist()
    ax.set_xticklabels(xlabels, ha='right')

    # horizontal line indicating the threshold
    ax.plot([-1, len(data)], [threshold, threshold], "k--", color = 'b')
    
    plt.title('Average Discogs users rating by album vs index', fontsize=18)
    plt.show()

    
def plot_albums_ratings_indexing(discog):
    threshold = discog['DISCOG_AVG_RATING'].mean()
    data = pd.pivot_table(discog,index='YEAR_ALBUM_DISPLAY',
                          values=['DISCOG_AVG_RATING'],
                          aggfunc = 'max')
    values = (np.array(data['DISCOG_AVG_RATING'])-threshold).tolist()
    data['indexing'] = values

    # plot it
    fig, ax = plt.subplots(figsize=(max(8,min(15,len(data)+2)),5))
    data['positive'] = data['indexing'] > 0
    data['indexing'].plot(kind='bar', 
                          color=data.positive.map({True: 'g', False: 'r'}), 
                          ax=ax, width=0.5, position=1)
    
    ax.set_ylabel('Album Discogs rating vs. average')
    ax.set_xlabel('Year/Album')

    ax.tick_params(axis='x', labelrotation=45)
    xlabels = data.index.tolist()
    ax.set_xticklabels(xlabels, ha='right')
    
    # horizontal line indicating the threshold
    ax.plot([-1, len(data)], [0, 0], "k--", color = 'b')
    
    plt.title('Average Discogs users rating by album vs index', fontsize=18)
    plt.show()
    
# function to run at click of the button
def show_discogs_users_charts(x):
    global discog_store
    discog_store = pd.read_csv('discog_store.csv')
    global bin_size

    # select current tab    
    global selected_section
    selected_section = 2
    # select sub tab
    global selection_tab_of_section_3
    selection_tab_of_section_3 = 0
    
    #clear previous output
    clear_output()
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    discog_filtered = discog_store[(discog_store['ARTIST_NAME']==artist)\
                      &(discog_store['YEAR_ALBUM'].isin(album_filter))].copy()
    plot_albums_discogs_popularity(discog_filtered)
    plot_albums_ratings(discog_filtered)
    plot_albums_ratings_indexing(discog_filtered)
    
    
    
#-------------------------------------------------------------------------------
# SECTION 3 | TAB 2 variables and functions
    
def create_chord_diag(df):
    '''
    Creating Chord diagram.
    @param - Dataframe
    @param - bin_size -> int [by default 10]
    
    @return - Chord_diagram using Chord Library
    '''
    # Creating period column 
    global bin_size
    get_period = add_period_column(df, bin_size)
    artist_nam = df['ARTIST_NAME'].iloc[0]
    # Flag Charted/Uncharted tracks
    get_period.loc[get_period['BILLBOARD_TRACK_RANK'] >= 1.0
                   , "Charted_Uncharted"
                  ] = 'Charted'
    
    get_period.loc[~(get_period['BILLBOARD_TRACK_RANK'] >= 1.0)
                   , "Charted_Uncharted"
                  ] = 'Uncharted'
    #Group By period and Chart_Unchart
    df_groupby = get_period[['period'
                              , 'BILLBOARD_TRACK_RANK'
                              , "Charted_Uncharted"]
                            ].groupby(['period', 'Charted_Uncharted']).size().reset_index()
    
    # Creating two pivot data
    pivot_data =  df_groupby.pivot(index = 'period'
                                    , columns = 'Charted_Uncharted'
                                    , values = 0)
    pivot_data2 =  df_groupby.pivot(index = 'Charted_Uncharted'
                                     , columns = 'period'
                                     , values = 0)
    
    # Appending two dataFrame
    df_final = pd.concat([pivot_data, pivot_data2], sort = True).fillna(0).astype(int)
    matrix = df_final.values.tolist()
    ls_col_nam = [col for col in df_final.columns]
#     {artist}
    plot = Chord(matrix
                 , ls_col_nam
                 , padding=0.05
                 , width = 600 if len(get_period["period"].unique()) < 5 else 500
                 , margin= 10 if len(get_period["period"].unique()) < 5 else 80
                 , wrap_labels= True if len(get_period["period"].unique()) < 5 else False
                ).to_html()
    display(widgets.HTML(value=f'''<h2><center><font color="black">Chord Diagram - Billboard 100 songs placement</center></h2>''',
                           layout=widgets.Layout(width="100%")))
    display(widgets.HTML(value=f'''<h3><center><font color="black">Artist: {artist_nam}</center></h3>''',
                           layout=widgets.Layout(width="100%")))
    display(IFrame(src="./out.html", width=1000, height=700))
    
# function to run at click of the button
def show_billboard_100_charts(x):
    global discog_store
    discog_store = pd.read_csv('discog_store.csv')
    global bin_size

    # select current tab    
    global selected_section
    selected_section = 2
    # select sub tab
    global selection_tab_of_section_3
    selection_tab_of_section_3 = 1
    
    #clear previous output
    clear_output()
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    
    discog_filtered = discog_store[(discog_store['ARTIST_NAME']==artist)\
                      &(discog_store['YEAR_ALBUM'].isin(album_filter))].copy()
    create_chord_diag(discog_filtered,)

    
#-------------------------------------------------------------------------------
# SECTION 3 | TAB 3 variables and functions
    
#TODO make chord diagram for albums
    
# function to run at click of the button
def show_billboard_album_charts(x):
    global discog_store
    discog_store = pd.read_csv('discog_store.csv')
    global bin_size

    # select current tab    
    global selected_section
    selected_section = 2
    # select sub tab
    global selection_tab_of_section_3
    selection_tab_of_section_3 = 2
    
    #clear previous output
    clear_output()
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    
    discog_filtered = discog_store[(discog_store['ARTIST_NAME']==artist)\
                      &(discog_store['YEAR_ALBUM'].isin(album_filter))].copy()
    ### placeholder for new function
    print('this is a placeholder for album charts chord diagram')
    

    
    
    
    
    
#-------------------------------------------------------------------------------
# # SECTION 4 | TAB 1 variables and functions

sentiment_dropdown1 = widgets.Dropdown(options=['albums', 'tracks by album',],
                                                value='albums',
                                                description='Display by:',
                                                disabled=False,)
sentiment_dropdown2 = widgets.Dropdown(options=[''],
                                                value='',
                                                description='',
                                                disabled=False,)
    
# function to run at click of the button_show_wordclouds
def show_sentiment_graphs(x):
    #clear previous output
    clear_output()
    print("Analysing the sentiment of the lyrics...")
    # select current tab    
    global selected_section
    selected_section = 3
    # select sub tab
    global selection_tab_of_section_4
    selection_tab_of_section_2 = 0
    global discog_filtered
    discog_filtered = discog_store[
        (discog_store['ARTIST_NAME']==artist)\
        &(discog_store['YEAR_ALBUM'].isin(album_filter))
    ].copy()
    
    clear_output()   
    UI()
    if sentiment_dropdown1.value == 'albums':
        advanced_analytics.plotDivergingBars(discog_filtered.reset_index(), 
                          'SENTIMENT_COMPOUND_SCORE', 
                          'YEAR_ALBUM')
    else:    
        advanced_analytics.plotDivergingBars(discog_filtered[discog_filtered.YEAR_ALBUM == sentiment_dropdown2.value].reset_index(), 
                          'SENTIMENT_COMPOUND_SCORE', 
                          'TRACK_TITLE')

# inner function to be triggered with a change of dropdown1 value
def adapt_UI(x):
    global discog_filtered, sentiment_dropdown2
    global selected_section
    selected_section = 3
    # select sub tab
    global selection_tab_of_section_4
    selection_tab_of_section_2 = 0
    clear_output()
    sentiment_dropdown2 = widgets.Dropdown(options=discog_filtered['YEAR_ALBUM'].unique(),
                                            value=discog_filtered['YEAR_ALBUM'].unique()[0],
                                            description='Select Album:',
                                            disabled=False,)
    UI()
#-------------------------------------------------------------------------------

def oldUI():
    #---------------------------------------------------------------------------
    # SECTION 1          "Get Data" (Get discography, select albums, get lyrics)
    #---------------------------------------------------------------------------
    # SECTION 1 | TAB 1    "Artist" (Get discography)  
    # global variable (input box)
    global artist_input
    # button = get artist discography
    button_get_discography = widgets.Button(description="Get discography")
    button_get_discography.on_click(get_discography)
    # wrap tab
    SECTION_1_TAB_1 = widgets.VBox([artist_input, button_get_discography,])
    #---------------------------------------------------------------------------
    # SECTION 1 | TAB 2     "Albums" (select albums to include in the analysis)
    # selector to include/exclude albums
    global album_selector
    # show current artist
    label_current_artist = widgets.HTML(value=f'''<b><font size = "+1">Selected\
    discography for <u>{artist}</u></b>''',
                           layout=widgets.Layout(width="100%"))
    # button to select/deselect
    text_select_deselect_all = widgets.Label(
        'Use checkboxes to toggle selection:',
        layout=widgets.Layout(width="80%"))
    button_select_deselect_all = widgets.Button(
        description="Select/deselect all")
    button_select_deselect_all.on_click(select_deselect_all)
    # button = confirm
    button_apply_selection = widgets.Button(description="Apply")
    button_apply_selection.on_click(apply_selection)
    # wrap elements
    SECTION_1_TAB_2 = widgets.VBox([label_current_artist, 
                              text_select_deselect_all, 
                              button_select_deselect_all,
                              album_selector, 
                              button_apply_selection,], 
                             layout=widgets.Layout(width="80%", 
                                                   padding = "10px"))  
    #---------------------------------------------------------------------------
    # SECTION 1 | TAB 3     "Time period" ( select time intervals for charts)
    # period size selection slider
    global period_selection_slider
    # button to update the period selection
    button_update_period_selection = widgets.Button(description="Confirm")
    button_update_period_selection.on_click(set_bin_size)
    # vertical block
    SECTION_1_TAB_3 = widgets.VBox([period_selection_slider, 
                                    button_update_period_selection,])
    
    #---------------------------------------------------------------------------
    # SECTION 1 build
    section_1_children = [SECTION_1_TAB_1, SECTION_1_TAB_2,SECTION_1_TAB_3]    
    section_1 = widgets.Tab(children=section_1_children)
    section_1.set_title(0, 'Artist')
    section_1.set_title(1, 'Albums')
    section_1.set_title(2, 'Time periods')
    section_1.selected_index = selection_tab_of_section_1    
    #---------------------------------------------------------------------------
    
    #---------------------------------------------------------------------------
    # SECTION 2          "Visualisations - single artist" 
    #---------------------------------------------------------------------------
    # SECTION 2 | TAB 1   "Basic Charts"
    # button to update chart
    button_show_basic_charts = widgets.Button(description="Show/refresh charts")
    button_show_basic_charts.on_click(show_basic_charts)
    # vertical block
    SECTION_2_TAB_1 = widgets.VBox([button_show_basic_charts,])
    #---------------------------------------------------------------------------   
    # SECTION 2 | TAB 2   "Wordclouds"
    # dropdown
    global wordcloud_by_selection_dropdown
    # button to update chart
    button_show_wordclouds = widgets.Button(description="Show")
    button_show_wordclouds.on_click(show_wordclouds)
    # vertical block
    SECTION_2_TAB_2 = widgets.VBox([wordcloud_by_selection_dropdown, 
                                    button_show_wordclouds,])
    #---------------------------------------------------------------------------
    # SECTION 2 | TAB 3   "Users and Ratings"
    # button to show charts
    button_users_ratings_charts = widgets.Button(description="Show")
    button_users_ratings_charts.on_click(show_users_ratings_charts)
    # vertical block
    SECTION_2_TAB_3 = widgets.VBox([button_users_ratings_charts,])
    #---------------------------------------------------------------------------
     # SECTION 2 | TAB 4   "Sentiment Analysis"
    global sentiment_dropdown1, sentiment_dropdown2
    # button to show charts
    button_sentiment_analysis = widgets.Button(description="Show")
    button_sentiment_analysis.on_click(show_sentiment_graphs)
    # vertical block
    # define tab depending on the value of the global variable
    if sentiment_dropdown1.value == 'tracks by album':
        SECTION_2_TAB_4 = widgets.VBox([sentiment_dropdown1,sentiment_dropdown2,button_sentiment_analysis, ])
    else:
        SECTION_2_TAB_4 = widgets.VBox([sentiment_dropdown1,button_sentiment_analysis])
    
    # trigger inner function when value of the dropdown1 changes
    sentiment_dropdown1.observe(adapt_UI, names='value')
    #---------------------------------------------------------------------------
    # SECTION 2 build
    section_2_children = [SECTION_2_TAB_1, 
                          SECTION_2_TAB_2, 
                          SECTION_2_TAB_3,
                          SECTION_2_TAB_4,] 
    section_2 = widgets.Tab()
    section_2.children = section_2_children
    section_2.set_title(0, 'Basic Charts')
    section_2.set_title(1, 'Wordclouds')
    section_2.set_title(2, 'Users and ratings')
    section_2.set_title(3, 'Sentiment analysis')
    section_2.selected_index = selection_tab_of_section_2 
    section_2_wrapper_label = widgets.HTML(
        value=f'''Current artist: <b>{artist}</b>''',
        layout=widgets.Layout(width="100%"))
    section_2_wrapper = widgets.VBox([section_2_wrapper_label, 
                                      section_2,])     
    #---------------------------------------------------------------------------
    
    
    #---------------------------------------------------------------------------
    # SECTION 3          "Visualisations - compare artists" 
    #---------------------------------------------------------------------------
    # SECTION 3 | TAB 1   "Select artists" 
    SECTION_3_TAB_1 = widgets.VBox()
    #---------------------------------------------------------------------------
    # SECTION 3 | TAB 1   "Basic charts"
    SECTION_3_TAB_2 = widgets.VBox()
    #---------------------------------------------------------------------------
    # SECTION 3 build
    section_3_children = [SECTION_3_TAB_1, 
                          SECTION_3_TAB_2,]
    section_3 = widgets.Tab()
    section_3.children = section_3_children
    section_3.set_title(0, 'Select Artists')
    section_3.set_title(1, 'Basic Charts')
    #---------------------------------------------------------------------------

     
    
    

    #---------------------------------------------------------------------------
    # FINAL UI compiler 
    #---------------------------------------------------------------------------
    UI = widgets.Accordion(children=[section_1,
                                     section_2_wrapper,
                                     section_3])
    UI.set_title(0, 'Configuration')
    UI.set_title(1, 'Visualisations - single artist')
    UI.set_title(2, 'Visualisations - compare artists')
    UI.selected_index = selected_section
    display(UI)
    #---------------------------------------------------------------------------

    
    
def UI():
    #---------------------------------------------------------------------------
    # SECTION 1            "Configuration" 
    #---------------------------------------------------------------------------
    # SECTION 1 | TAB 1    "Artist" (Get discography)  
    # global variable (input box)
    global artist_input
    # button = get artist discography
    button_get_discography = widgets.Button(description="Get discography")
    button_get_discography.on_click(get_discography)
    # wrap tab
    SECTION_1_TAB_1 = widgets.VBox([artist_input, button_get_discography,])
    #---------------------------------------------------------------------------
    # SECTION 1 | TAB 2     "Albums" (select albums to include in the analysis)
    # selector to include/exclude albums
    global album_selector
    # show current artist
    label_current_artist = widgets.HTML(value=f'''<b><font size = "+1">Selected\
    discography for <u>{artist}</u></b>''',
                           layout=widgets.Layout(width="100%"))
    # button to select/deselect
    text_select_deselect_all = widgets.Label(
        'Use checkboxes to toggle selection:',
        layout=widgets.Layout(width="80%"))
    button_select_deselect_all = widgets.Button(
        description="Select/deselect all")
    button_select_deselect_all.on_click(select_deselect_all)
    # button = confirm
    button_apply_selection = widgets.Button(description="Apply")
    button_apply_selection.on_click(apply_selection)
    # wrap elements
    SECTION_1_TAB_2 = widgets.VBox([label_current_artist, 
                              text_select_deselect_all, 
                              button_select_deselect_all,
                              album_selector, 
                              button_apply_selection,], 
                             layout=widgets.Layout(width="80%", 
                                                   padding = "10px"))  
    #---------------------------------------------------------------------------
    # SECTION 1 | TAB 3     "Time period" ( select time intervals for charts)
    # period size selection slider
    global period_selection_slider
    # button to update the period selection
    button_update_period_selection = widgets.Button(description="Confirm")
    button_update_period_selection.on_click(set_bin_size)
    # vertical block
    SECTION_1_TAB_3 = widgets.VBox([period_selection_slider, 
                                    button_update_period_selection,])
    
    #---------------------------------------------------------------------------
    # SECTION 1 build
    section_1_children = [SECTION_1_TAB_1, 
                          SECTION_1_TAB_2,
                          SECTION_1_TAB_3]    
    section_1 = widgets.Tab(children=section_1_children)
    section_1.set_title(0, 'Artist')
    section_1.set_title(1, 'Albums')
    section_1.set_title(2, 'Time periods')
    section_1.selected_index = selection_tab_of_section_1    
    #---------------------------------------------------------------------------
    
    #---------------------------------------------------------------------------
    # SECTION 2          "Visualisations - Overview and Lexical Diversity" 
    #---------------------------------------------------------------------------
    
    #---------------------------------------------------------------------------
    # SECTION 2 | TAB 1   "Overview"
    # button to update chart
    button_show_basic_charts = widgets.Button(description="Show/refresh charts")
    button_show_basic_charts.on_click(show_basic_charts)
    # vertical block
    SECTION_2_TAB_1 = widgets.VBox([button_show_basic_charts,])
    #---------------------------------------------------------------------------
    # SECTION 2 | TAB 2   "Lexical Diversity"
    # button to update chart
    button_show_lexical_diversity = widgets.Button(description="Show/refresh charts")
    button_show_lexical_diversity.on_click(show_lexical_diversity)
    # vertical block
    SECTION_2_TAB_2 = widgets.VBox([button_show_lexical_diversity,])
    #---------------------------------------------------------------------------   
    # SECTION 2 | TAB 3   "Wordclouds"
    # dropdown
    global wordcloud_by_selection_dropdown
    # button to update chart
    button_show_wordclouds = widgets.Button(description="Show")
    button_show_wordclouds.on_click(show_wordclouds)
    # vertical block
    SECTION_2_TAB_3 = widgets.VBox([wordcloud_by_selection_dropdown, 
                                    button_show_wordclouds,])
    #---------------------------------------------------------------------------
    # SECTION 2 build
    section_2_children = [SECTION_2_TAB_1, 
                          SECTION_2_TAB_2, 
                          SECTION_2_TAB_3,] 
    section_2 = widgets.Tab()
    section_2.children = section_2_children
    section_2.set_title(0, 'Basic Charts')
    section_2.set_title(1, 'Lexical Diversity')
    section_2.set_title(2, 'Wordclouds')
    section_2.selected_index = selection_tab_of_section_2 
    section_2_wrapper_label = widgets.HTML(
        value=f'''Current artist: <b>{artist}</b>''',
        layout=widgets.Layout(width="100%"))
    section_2_wrapper = widgets.VBox([section_2_wrapper_label, 
                                      section_2,])     
    #---------------------------------------------------------------------------
    
    
    
    #---------------------------------------------------------------------------
    # SECTION 3          "Visualisations - Ratings and Sucess" 
    #---------------------------------------------------------------------------    
    #---------------------------------------------------------------------------
    # SECTION 3 | TAB 1   "Discogs Ratings"
    # button to show charts
    button_discogs_users_charts = widgets.Button(description="Show")
    button_discogs_users_charts.on_click(show_discogs_users_charts)
    # vertical block
    SECTION_3_TAB_1 = widgets.VBox([button_discogs_users_charts,])
    #---------------------------------------------------------------------------
    # SECTION 3 | TAB 2   "Billboard 100"
    # button to show charts
    button_billboard_100_charts = widgets.Button(description="Show")
    button_billboard_100_charts.on_click(show_billboard_100_charts)
    # vertical block
    SECTION_3_TAB_2 = widgets.VBox([button_billboard_100_charts,])
    #---------------------------------------------------------------------------                     
    # SECTION 3 | TAB 3   "Billboard Albums"
    # button to show charts
    button_billboard_albums_charts = widgets.Button(description="Show")
    button_billboard_albums_charts.on_click(show_billboard_album_charts)
    # vertical block
    SECTION_3_TAB_3 = widgets.VBox([button_billboard_albums_charts,])
    #---------------------------------------------------------------------------                          
    # SECTION 3 build
    section_3_children = [SECTION_3_TAB_1, 
                          SECTION_3_TAB_2, 
                          SECTION_3_TAB_3,] 
    section_3 = widgets.Tab()
    section_3.children = section_3_children
    section_3.set_title(0, 'Discogs Ratings')
    section_3.set_title(1, 'Billboard 100')
    section_3.set_title(2, 'Billboard Albums')
    section_3.selected_index = selection_tab_of_section_3 
    section_3_wrapper_label = widgets.HTML(
        value=f'''Current artist: <b>{artist}</b>''',
        layout=widgets.Layout(width="100%"))
    section_3_wrapper = widgets.VBox([section_3_wrapper_label, 
                                      section_3,])     
    #---------------------------------------------------------------------------                          
                          
                          
                          
    #---------------------------------------------------------------------------
    # SECTION 4          "Visualisations - Sentiment Analysis" 
    #---------------------------------------------------------------------------    
    #---------------------------------------------------------------------------
    # SECTION 4 | TAB 1   "Albums and Songs Sentiment"
    global sentiment_dropdown1, sentiment_dropdown2
    # button to show charts
    button_sentiment_analysis = widgets.Button(description="Show")
    button_sentiment_analysis.on_click(show_sentiment_graphs)
    # vertical block
    # define tab depending on the value of the global variable
    if sentiment_dropdown1.value == 'tracks by album':
        SECTION_4_TAB_1 = widgets.VBox([sentiment_dropdown1,sentiment_dropdown2,button_sentiment_analysis, ])
    else:
        SECTION_4_TAB_1 = widgets.VBox([sentiment_dropdown1,button_sentiment_analysis])
    
    # trigger inner function when value of the dropdown1 changes
    sentiment_dropdown1.observe(adapt_UI, names='value')

    #---------------------------------------------------------------------------                          
    # SECTION 4 | TAB 2   "Sentiment and Charts"                                        
    SECTION_4_TAB_2 = widgets.VBox()
                          
    #---------------------------------------------------------------------------
    # SECTION 4 build
    section_4_children = [SECTION_4_TAB_1, 
                          SECTION_4_TAB_2,] 
    section_4 = widgets.Tab()
    section_4.children = section_4_children
    section_4.set_title(0, 'Lyrics Sentiment')
    section_4.set_title(1, 'Sentiment vs Charts')

    section_4.selected_index = selection_tab_of_section_4 
    section_4_wrapper_label = widgets.HTML(
        value=f'''Current artist: <b>{artist}</b>''',
        layout=widgets.Layout(width="100%"))
    section_4_wrapper = widgets.VBox([section_4_wrapper_label, 
                                      section_4,])     
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # FINAL UI compiler 
    #---------------------------------------------------------------------------
    UI = widgets.Accordion(children=[section_1,
                                     section_2_wrapper,
                                     section_3_wrapper,
                                     section_4_wrapper])
    UI.set_title(0, 'Configuration')
    UI.set_title(1, 'Visualisations - Overview and Lexical Diversity')
    UI.set_title(2, 'Visualisations - Ratings and Sucess')
    UI.set_title(3, 'Visualisations - Sentiment Analysis')
    UI.selected_index = selected_section
    display(UI)
    #---------------------------------------------------------------------------
    
    
    