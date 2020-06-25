print('Loading...')

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from IPython.display import clear_output, display
# UI
import ipywidgets as widgets

# other fuctions
from functions import get_discogs
from functions import get_lyrics
from functions import plot_wordcloud

# word processing
import re
import os
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = stopwords.words('english')
clear_output()
import string

##################################################################
#import sample discography

##################################################################

# default selected tab in the UI
selected_tab = 0
selected_sub_tab_1 = 0
selected_sub_tab_2 = 0

#----------------------------------------------------------------------------------------
# UI SECTION 1

# global var for discog
discog = ''
#global var for artist
artist = ''
#global widget to type artist name
artist_input = widgets.Text()
# define function to overwrite artist from user input
def set_artist(x):
    global artist
    artist = x
# function to set list of albums into the selector
def set_album_selector(albums,selected):
    global album_selector
    album_selector.options = albums
    album_selector.value = selected
    
discog_store = []


# function to run at click of the button_1    
def button_1_func(x):
    #clear previous output
    clear_output()
    print("Looking for best match for '" + str(artist_input.value) +"'")
    time.sleep(2)
    global discog_store
    try:
        discog_store = pd.read_csv('discog_store.csv')
    except:
        pass
        
    global artist 
    
    #try to overwrite artist artist found as best match from DISCOGS  
    try:
        set_artist(get_discogs.getArtistID(artist_input.value)[1])
    # if no match found from discogs, stop and print a message
    except:
        display(widgets.HTML(value=f'''<b><font color="red">No match found, please try again </b>''',
                           layout=widgets.Layout(width="100%")))
        #print(widgets"No match found, please try again")
        return UI()
    
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
    discog['YEAR_ALBUM'] = "[" + discog['YEAR'].astype(str) + "] " + discog['ALBUMS']
    
    #clear previous output
    clear_output()
    
    #select tab
    global selected_tab
    selected_tab = 0
    # select next sub tab
    global selected_sub_tab_1
    selected_sub_tab_1 = 1
    
    # set album selecor content
    
    #overwrite album_filter with current selection
    global album_filter    
    set_album_filter(discog[discog['EXCLUDE_ALBUM'] != True]['YEAR_ALBUM'].unique().tolist())
               
    global album_selector_alt 
    
    set_album_selector_alt(discog['YEAR_ALBUM'].unique().tolist(), album_filter)
    # display UI
    UI()
    
 
#----------------------------------------------------------------------------------------
# UI SECTION 2

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
                                            layout={'margin' : '-2px', 'width' : 'initial'}) for album in albums}
    options = [options_dict[album] for album in albums]
    for option in options:
        if option.description in albums_filter:
            option.value = True
    options_widget = widgets.VBox(options, layout={'overflow': 'scroll', 'max_height': '300px', 'width' : 'initial'})
    multi_select = widgets.VBox([options_widget], layout=widgets.Layout(padding = "20px"))
    return multi_select

def set_album_selector_alt(options, options_filter):
    global album_selector_alt
    album_selector_alt = multi_checkbox_widget(options,options_filter) 

album_selector_alt = multi_checkbox_widget([],[])
import time

def button_2_1_func(x):
    #clear previous output
    clear_output() 
    global album_selector_alt 
    if album_selector_alt.children[0].children[0].value == True:
        set_album_selector_alt(discog['YEAR_ALBUM'].unique().tolist(), [])
    else:
        set_album_selector_alt(discog['YEAR_ALBUM'].unique().tolist(), discog['YEAR_ALBUM'].unique().tolist())
    # select this tab    
    global selected_tab
    selected_tab = 1
    # select sub tab
    global selected_sub_tab_2
    selected_sub_tab_2 = 0
    
    # display UI
    UI()
    
def button_2_alt_func(x):
    global discog
    global discog_store

    
    #apply user selections, overwrite album_filter with current selection
    global album_selector_alt 
    global album_filter 
    selected = []
    # read user input
    for album in album_selector_alt.children[0].children:
        # overwrite EXCLUDE_ALBUM flag
        discog.loc[discog['YEAR_ALBUM'] == album.description, 'EXCLUDE_ALBUM'] = not album.value
        #make a list of selected albums
        if album.value == True:
            selected.append(album.description)
    # set filter = list of selected albums
    set_album_filter(selected)
    # reset selector to keep the actual selections
    set_album_selector_alt(discog['YEAR_ALBUM'].unique().tolist(), selected)
    
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
            discog_store = discog_store.append(discog, ignore_index=True, sort=False)
        else:
            discog_store = discog_store[discog_store['ARTIST_NAME'] != artist].append(discog, ignore_index=True, sort=False)
    
    try:
        discog_store.to_csv('discog_store.csv', index = False)
    except PermissionError:
        clear_output()
        display(widgets.HTML(value=f'''<b><font color="red">Permission denied: make sure 'discog_store.csv' is closed and try again </b>''',
                           layout=widgets.Layout(width="100%")))
        return UI()
        
    
    #get lyrics
    print('Getting the lyrics, please hold on')
    
    if len(discog_store[(discog_store['ARTIST_NAME'] == artist)
                    & (discog_store["EXCLUDE_ALBUM"] == False) 
                    & (discog_store["EXCLUDE_SONG"] == False)]) > 0:
        if "LYRICS" not in discog_store.columns:
            lyrics_data = get_lyrics.getLyrics(discog_store[discog_store['ARTIST_NAME'] == artist])
        elif len(discog_store[(discog_store['ARTIST_NAME'] == artist)
                              & (discog_store["EXCLUDE_ALBUM"] == False)
                              & (discog_store["EXCLUDE_SONG"] == False)
                              &(~discog_store['LYRICS'].notnull())]) > 0:
            lyrics_data = get_lyrics.getLyrics(discog_store[(discog_store['ARTIST_NAME'] == artist) \
                                                            &(~discog_store['LYRICS'].notnull())])
        else:
            lyrics_data = []
    else:
        lyrics_data = []
    print('processing and cleaning, please hold on')
    if len(lyrics_data) != 0:
        for i,r in lyrics_data.iterrows():
            discog_store.loc[(discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                             (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']), "LYRICS"] = r['LYRICS']
        # add column with lyrics with removed stopwords
        #discog_store["LYRICS_CLEAN"] = discog_store['LYRICS'].astype(str).apply(lambda x: ' '.join(list(word for word in x.lower().split() if word not in stop_words)))
        discog_store["LYRICS_CLEAN"] = discog_store['LYRICS'].astype(str).apply(lambda x: ' '.join(list(word for word in re.findall(r"[\w]+|[^\s\w]",x.lower()) if word not in stop_words)))       
        # remove punctuation
        discog_store["LYRICS_CLEAN"] = discog_store['LYRICS_CLEAN'].str.replace('[^\w\s] ','')
            
        #list unique clean words
        discog_store["LYRICS_CLEAN_UNIQUE"] = discog_store['LYRICS_CLEAN'].astype(str).apply(lambda x: list(set(x.split())))
        #count unique clean words
        discog_store["LYRICS_CLEAN_UNIQUE_COUNT"] =discog_store['LYRICS_CLEAN_UNIQUE'].apply(lambda x: len(x))
            
    
    # write the updated content
    try:
        discog_store.to_csv('discog_store.csv', index = False)
    except PermissionError:
        clear_output()
        display(widgets.HTML(value=f'''<b><font color="red">Permission denied: make sure 'discog_store.csv' is closed and try again </b>''',
                           layout=widgets.Layout(width="100%")))
        return UI()
        
    
    clear_output()
    # select tab
    global selected_tab
    selected_tab = 1
    # select sub tab
    global selected_sub_tab_2
    selected_sub_tab_2 = 0
    
    # display UI
    UI()    
    

#----------------------------------------------------------------------------------------
# UI SECTION 3

def generate_period_bins(discog, bin_size):
    '''returns list of period bins starting 0th year of the decade of first release'''
    bins = []
    start_year = int(str(discog['YEAR'].min())[:3]+'0')
    last_year = int(discog['YEAR'].max()) + int(str(100 - int(str(discog['YEAR'].max())[2:]))[-1])
    year = start_year
    while year <= last_year:
        bins.append(str(year) + '-' + str(year + bin_size-1))
        year += bin_size
    return bins

def unique_per_period(discog, column, bin_size):
    '''returns a dataframe with count of unique values within a column by defined bin size'''
    data = {'period' : generate_period_bins(discog, bin_size),
            column : []}
    for period in data['period']:
        data[column].append(len(discog[(discog['YEAR'].astype(int) >= int(period[:4])) \
                                       & (discog['YEAR'].astype(int) <= int(period[5:]))][column].unique()))  
    
    # filter out all but one of periods that are empty before first and after last record
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
            counter = counter + output.iloc[i]['data_flag'] + output.iloc[i+1]['data_flag']
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
            counter = counter + output.iloc[i]['data_flag'] + output.iloc[i+1]['data_flag']
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
    '''returns a merged dataframe by period with counts of albums and songs per period'''
    data_albums = unique_per_period(discog, 'ALBUMS', bin_size)
    data_songs = unique_per_period(discog, 'TRACK_TITLE', bin_size)
    return data_albums.merge(data_songs, on = 'period')

def add_period_column(discog, bin_size):
    '''adds column with period info without any other modifications'''
    period_col_data = []
    bins = generate_period_bins(discog, bin_size)
    for i, r in discog.iterrows():
        for period in bins:
            if int(r['YEAR']) >= int(period[:4]) and int(r['YEAR']) <= int(period[5:]):
                period_col_data.append(period)
    discog['period'] = period_col_data
    return discog
                                                                 
def plot_albums_songs_per_period(discog, bin_size):
    '''plots the number of albums and songs per period'''
    
    data = album_song_count_per_period(discog, bin_size)
    
    fig, ax1 = plt.subplots(figsize=(8,5))

    color = 'tab:red'
    ax1.set_xlabel(str(bin_size) + '-year period')
    ax1.set_ylabel('number of albums', color=color)

    ax1.plot(data['period'], data['ALBUMS'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('number of songs', color=color)  # we already handled the x-label with ax1
    ax2.plot(data.index.tolist(), data['TRACK_TITLE'], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    plt.title('Albums and songs count by period', fontsize=18)
    plt.show()

def plot_albums_songs_per_period_bar(discog, bin_size):
    '''plots the number of albums and songs per period'''
    
    width = 0.2
    data = album_song_count_per_period(discog, bin_size).set_index('period')
    
    fig, ax1 = plt.subplots(figsize=(8,5))

    color = 'tab:red'

    ax1.set_ylabel('number of albums', color=color)
    #ax1.plot(data.period, data.album, color=color)
    data['ALBUMS'].plot(kind='bar', color='red', ax=ax1, width=width, position=1)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.set_xlabel(str(bin_size) + '-year period')
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('number of songs', color=color)  # we already handled the x-label with ax1
    #ax2.plot(data.index.tolist(), data.track_title, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    data['TRACK_TITLE'].plot(kind='bar', color='blue', ax=ax2, width=width, position=0)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    plt.title('Albums and songs count by period', fontsize=18)
    plt.show()
    
def pirate_plot(discog, bin_size):
    data = add_period_column(discog, bin_size)
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(8,5))
    ax = sns.boxplot(x="period", y="LYRICS_CLEAN_UNIQUE_COUNT", data=data)
    ax = sns.stripplot(x="period", y="LYRICS_CLEAN_UNIQUE_COUNT", data=data, color=".25")
    ax.set_xlabel('Period')
    ax.set_ylabel('Number of unique words (excl. stopwords)')
    plt.title('Lexical diversity', fontsize=18)
    plt.show()

def violin_plot(discog, bin_size):
    data = add_period_column(discog, bin_size)
    # Draw Plot
    plt.figure(figsize=(8,5), dpi= 80)
    sns.violinplot(x='period', y='LYRICS_CLEAN_UNIQUE_COUNT', data=data, scale='width', inner='quartile', cut=0)
    # Decoration
    plt.title('Lexical diversity', fontsize=18)
    plt.ylabel('Number of unique words (excl. stopwords)')
    plt.xlabel('Period')
    plt.show()


# set bin_size var with default 10
bin_size = 10
# define function to overwrite bin_size from slider input
def set_bin_size(x):
    global bin_size
    bin_size = x

# function to run at click of the button_3
def button_3_func(x):
    global bin_size
    #overwrite bin_size with current selection of the slider
    set_bin_size(slider_1.value)
    #clear previous output
    clear_output()
    # select current tab    
    global selected_tab
    selected_tab = 1
    # select sub tab
    global selected_sub_tab_2
    selected_sub_tab_2 = 0
    
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    discog_filtered = discog_store[(discog_store['ARTIST_NAME']==artist)\
                                   &(discog_store['YEAR_ALBUM'].isin(album_filter))].copy()
    #display chart using the new bin_size
    #plot_albums_songs_per_period(discog_filtered, bin_size)
    plot_albums_songs_per_period_bar(discog_filtered, bin_size)
    #pirate_plot(discog_filtered, bin_size)
    violin_plot(discog_filtered, bin_size)


#defining a slider for bin_size selector
slider_1 = widgets.IntSlider(
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


    
    

#----------------------------------------------------------------------------------------
# UI SECTION 4  
        
# function to run at click of the button_4
def button_4_func(x):
    global bin_size
    #overwrite bin_size with current selection of the slider
    set_bin_size(slider_1.value)
    #clear previous output
    clear_output()
    # select current tab    
    global selected_tab
    selected_tab = 1
    # select sub tab
    global selected_sub_tab_2
    selected_sub_tab_2 = 1
    
    # display UI
    UI()
    #filter dataset
    global discog_filtered
    discog_filtered = discog_store[(discog_store['ARTIST_NAME']==artist)\
                                   &(discog_store['YEAR_ALBUM'].isin(album_filter))].copy()
    
    data = add_period_column(discog_filtered, bin_size)
    
    if dropdown_1.value == 'period':
        plot_wordcloud.createWordCloud(data[~data['LYRICS_CLEAN'].isnull()], 'period')
    elif dropdown_1.value ==  'album':
        plot_wordcloud.createWordCloud(data[~data['LYRICS_CLEAN'].isnull()], 'YEAR_ALBUM')
    

dropdown_1 = widgets.Dropdown(options=['period', 'album',],
                              value='period',
                              description='Display by:',
                              disabled=False,)  

#----------------------------------------------------------------------------------------
# UI SECTION 5 
        
def plot_albums_discogs_popularity(discog):
    '''plots Discogs registered owners and average ratings'''
    
    width = 0.2
    data = pd.pivot_table(discog, 
                          index = 'YEAR_ALBUM', 
                          values = ['DISCOG_PPL_HAVING', 'DISCOG_AVG_RATING'],
                          aggfunc = 'max')
    
    fig, ax1 = plt.subplots(figsize=(max(8,min(15,len(data)+2)),5))

    color = 'y'

    ax1.set_ylabel('Discogs owners', color=color)
    #ax1.plot(data.period, data.album, color=color)
    data['DISCOG_PPL_HAVING'].plot(kind='bar', color=color, ax=ax1, width=width, position=1)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.set_xlabel('Year/Album')
    xlabels = data.index.tolist()
    ax1.set_xticklabels(xlabels, ha='right')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'g'
    ax2.set_ylabel('Discogs average rating', color=color)  # we already handled the x-label with ax1
    #ax2.plot(data.index.tolist(), data.track_title, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    data['DISCOG_AVG_RATING'].plot(kind='bar', color=color, ax=ax2, width=width, position=0)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    #ax1.xticks(ha='right')
    plt.title('Discogs users - owners and average ratings', fontsize=18)
    plt.show()
    
def plot_albums_ratings(discog):
    threshold = discog['DISCOG_AVG_RATING'].mean()
    data = pd.pivot_table(discog,index='YEAR_ALBUM',values=['DISCOG_AVG_RATING'],aggfunc = 'max')
    values = np.array(data['DISCOG_AVG_RATING'].tolist())

    # plot it
    fig, ax = plt.subplots(figsize=(max(8,min(15,len(data)+2)),5))

    data['DISCOG_AVG_RATING'].plot(kind='bar', color='y', ax=ax, width=0.5, position=1)
    ax.set_ylabel('Avg. Discogs user rating')
    ax.set_xlabel('Year/Album')

    ax.tick_params(axis='x', labelrotation=45)
    xlabels = data.index.tolist()
    ax.set_xticklabels(xlabels, ha='right')

    # horizontal line indicating the threshold
    ax.plot([-1, len(data)], [threshold, threshold], "k--", color = 'b')
    
    plt.title('Average Discogs users rating by album vs index', fontsize=18)
    plt.show()
    
# function to run at click of the button_5
def button_5_func(x):
    global discog_store
    discog_store = pd.read_csv('discog_store.csv')
    global bin_size

    # select current tab    
    global selected_tab
    selected_tab = 1
    # select sub tab
    global selected_sub_tab_2
    selected_sub_tab_2 = 2
    
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

#----------------------------------------------------------------------------------------
# display UI
    
def UI():
    # SECTION 1 = lyrics getter
    # input box = insert artist
    # button = get artist discography
    global artist_input
    button_1 = widgets.Button(description="Get discography")
    button_1.on_click(button_1_func)
    SECTION_1 = widgets.VBox([artist_input, button_1,])
    

    # SECTION 2 alternative
    # list of albums to include in the analysis
    # selector to include/exclude albums
    # button = confirm
    global album_selector_alt
    button_2 = widgets.Button(description="Apply")
    button_2.on_click(button_2_alt_func)
    label_2 = widgets.HTML(value=f'''<b><font size = "+1">Selected discography for <u>{artist}</u></b>''',
                           layout=widgets.Layout(width="100%"))
    text_2 = widgets.Label('Use checkboxes to toggle selection:', layout=widgets.Layout(width="80%"))
    button_2_1 = widgets.Button(description="Select/deselect all")
    button_2_1.on_click(button_2_1_func)
    SECTION_2 = widgets.VBox([label_2, text_2, button_2_1,album_selector_alt, button_2,], 
                             layout=widgets.Layout(width="80%", padding = "10px"))  
    
    # SECTION 3 = chart plots
    # chart 1
    global slider_1
    # button to update chart
    button_3 = widgets.Button(description="Show/refresh charts")
    button_3.on_click(button_3_func)
    
    # vertical block
    SECTION_3 = widgets.VBox([slider_1, button_3,])
 
    # SECTION 4 = wordclouds
    # dropdown
    global dropdown_1
    # button to update chart
    button_4 = widgets.Button(description="Show")
    button_4.on_click(button_4_func)
    
    # vertical block
    SECTION_4 = widgets.VBox([dropdown_1, button_4,])
    
    # SECTION 5 = wordclouds
    # button to update chart
    button_5 = widgets.Button(description="Show")
    button_5.on_click(button_5_func)
    
    # vertical block
    SECTION_5 = widgets.VBox([button_5,])
    
    
    #tab_contents = ['Chart_1',]
    #children = [SECTION_1, SECTION_2, SECTION_3, SECTION_4, SECTION_5,]    
    #accordion = widgets.Accordion(children=children)
    #accordion.set_title(0, 'Get Discography')
    #accordion.set_title(1, 'Select albums')
    #accordion.set_title(2, 'Basic Charts')
    #accordion.set_title(3, 'Wordclouds')
    #accordion.set_title(4, 'Users and ratings')
    #accordion.selected_index = selected_tab
    #display(accordion)
    
    #children = [SECTION_1, SECTION_2, SECTION_3, SECTION_4, SECTION_5,] 
    #tab = widgets.Tab()
    #tab.children = children
    #tab.set_title(0, 'Get Discography')
    #tab.set_title(1, 'Select albums')
    #tab.set_title(2, 'Basic Charts')
    #tab.set_title(3, 'Wordclouds')
    #tab.set_title(4, 'Users and ratings')
    #tab.selected_index = selected_tab
    #display(tab)

    #tab_contents = ['Chart_1',]
    children_1 = [SECTION_1, SECTION_2]    
    tab1 = widgets.Tab(children=children_1)
    tab1.set_title(0, 'Artist')
    tab1.set_title(1, 'Albums')
    tab1.selected_index = selected_sub_tab_1
    #display(accordion)
    
    children_2 = [SECTION_3, SECTION_4, SECTION_5,] 
    tab2 = widgets.Tab()
    tab2.children = children_2
    tab2.set_title(0, 'Basic Charts')
    tab2.set_title(1, 'Wordclouds')
    tab2.set_title(2, 'Users and ratings')
    tab2.selected_index = selected_sub_tab_2

    UI = widgets.Accordion(children=[tab1,tab2])
    UI.set_title(0, 'Get Data')
    UI.set_title(1, 'Visualisations')
    UI.selected_index = selected_tab
    display(UI)
    