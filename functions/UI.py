import matplotlib.pyplot as plt
import pandas as pd
import time
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from IPython.display import clear_output, display
# UI
import ipywidgets as widgets

# other fuctions
from functions import get_discogs
from functions import get_lyrics

##################################################################
#import sample discography

##################################################################

# default selected tab in the UI
selected_tab = 0

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
    
    #clear previous output
    clear_output()
    
    # select next tab
    global selected_tab
    selected_tab = 1
    # set album selecor content
    
    #overwrite album_filter with current selection
    global album_filter    
    set_album_filter(discog[discog['EXCLUDE_ALBUM'] != True]['ALBUMS'].unique().tolist())
               
    global album_selector_alt 
    set_album_selector_alt(discog['ALBUMS'].unique().tolist(), album_filter)
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
        discog.loc[discog['ALBUMS'] == album.description, 'EXCLUDE_ALBUM'] = not album.value
        #make a list of selected albums
        if album.value == True:
            selected.append(album.description)
    # set filter = list of selected albums
    set_album_filter(selected)
    # reset selector to keep the actual selections
    set_album_selector_alt(discog['ALBUMS'].unique().tolist(), selected)
    
    #filter dataset
    global discog_filtered
    discog_filtered = discog[discog['ALBUMS'].isin(album_filter)].copy()
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
    
    discog_store.to_csv('discog_store.csv', index = False)
        
    
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
        
    if len(lyrics_data) != 0:
        for i,r in lyrics_data.iterrows():
            discog_store.loc[(discog_store['ARTIST_NAME'] == r['ARTIST_NAME']) &
                             (discog_store['TRACK_TITLE'] == r['TRACK_TITLE']), "LYRICS"] = r['LYRICS']
    # write the updated content
    discog_store.to_csv('discog_store.csv', index = False)
    
    clear_output()
    # select next tab    
    global selected_tab
    selected_tab = 2
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
    while year < last_year:
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
    return pd.DataFrame.from_dict(data)

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
            if r['year'] >= int(period[:4]) and r['YEAR'] <= int(period[5:]):
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

    plt.show()
    
def pirate_plot(discog, bin_size):
    data = add_period_column(discog, bin_size)
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(8,5))
    ax = sns.boxplot(x="period", y="unique_words", data=data)
    ax = sns.stripplot(x="period", y="unique_words", data=data, color=".25")
    
def violin_plot(discog, bin_size):
    data = add_period_column(discog, bin_size)
    # Draw Plot
    plt.figure(figsize=(8,5), dpi= 80)
    sns.violinplot(x='period', y='unique_words', data=data, scale='width', inner='quartile', cut=0)
    # Decoration
    plt.title('Lexical diversity', fontsize=22)
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
    # display UI
    UI()
    #display chart using the new bin_size
    plot_albums_songs_per_period(discog_filtered, bin_size)
    plot_albums_songs_per_period_bar(discog_filtered, bin_size)
    #pirate_plot(discog_filtered, bin_size)
    #violin_plot(discog_filtered, bin_size)

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
    SECTION_2 = widgets.VBox([label_2, text_2, album_selector_alt, button_2,], 
                             layout=widgets.Layout(width="80%", padding = "10px"))  
    
    # SECTION 3 = chart plots
    # chart 1
    global slider_1
    # button to update chart
    button_3 = widgets.Button(description="Show/refresh chart")
    button_3.on_click(button_3_func)
    
    # vertical block
    SECTION_3 = widgets.VBox([slider_1, button_3,])
       
    #tab_contents = ['Chart_1',]
    children = [SECTION_1, SECTION_2, SECTION_3,]    
    accordion = widgets.Accordion(children=children)
    accordion.set_title(0, 'Get Discography')
    accordion.set_title(1, 'Select albums')
    accordion.set_title(2, 'Show Stats')
    accordion.selected_index = selected_tab
    display(accordion)
