import matplotlib.pyplot as plt
import pandas as pd
import time
from matplotlib.ticker import MaxNLocator

from IPython.display import clear_output

##################################################################
#import sample discography
discog = pd.read_csv('sample_discography.csv')
##################################################################


def generate_period_bins(discog, bin_size):
    '''returns list of period bins starting 0th year of the decade of first release'''
    bins = []
    start_year = int(str(discog.year.min())[:3]+'0')
    last_year = int(str(discog.year.max())[:2]+str(int(str(discog.year.max())[2])+1)+'0')
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
        data[column].append(len(discog[(discog['year'] >= int(period[:4])) \
                                       & (discog['year'] <= int(period[5:]))][column].unique()))   
    return pd.DataFrame.from_dict(data)


def album_song_count_per_period(discog, bin_size):
    '''returns a merged dataframe by period with counts of albums and songs per period'''
    data_albums = unique_per_period(discog, 'album', bin_size)
    data_songs = unique_per_period(discog, 'track_title', bin_size)
    return data_albums.merge(data_songs, on = 'period')


def plot_albums_songs_per_period(discog, bin_size):
    '''plots the number of albums and songs per period'''
    
    data = album_song_count_per_period(discog, bin_size)
    
    fig, ax1 = plt.subplots(figsize=(8,4))

    color = 'tab:red'
    ax1.set_xlabel(str(bin_size) + '-year period')
    ax1.set_ylabel('number of albums', color=color)
    ax1.plot(data.period, data.album, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('number of songs', color=color)  # we already handled the x-label with ax1
    ax2.plot(data.index.tolist(), data.track_title, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    plt.show()

def plot_albums_songs_per_period_bar(discog, bin_size):
    '''plots the number of albums and songs per period'''
    
    width = 0.2
    data = album_song_count_per_period(discog, bin_size).set_index('period')
    
    fig, ax1 = plt.subplots(figsize=(8,4))

    color = 'tab:red'

    ax1.set_ylabel('number of albums', color=color)
    #ax1.plot(data.period, data.album, color=color)
    data.album.plot(kind='bar', color='red', ax=ax1, width=width, position=1)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.set_xlabel(str(bin_size) + '-year period')
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('number of songs', color=color)  # we already handled the x-label with ax1
    #ax2.plot(data.index.tolist(), data.track_title, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label may be slightly clipped
    data.track_title.plot(kind='bar', color='blue', ax=ax2, width=width, position=0)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) 

    plt.show()
    
# set bin_size var with default 10
bin_size = 10
# define function to overwrite bin_size from slider input
def set_bin_size(x):
    global bin_size
    bin_size = x

# function to run at click of the button_1
def button_1_func(x):
    global bin_size
    #overwrite bin_size with current selection of the slider
    set_bin_size(slider_1.value)
    #clear previous output
    clear_output()
    # display UI
    plots()
    #display chart using the new bin_size
    plot_albums_songs_per_period(discog, bin_size)
    plot_albums_songs_per_period_bar(discog, bin_size)

    
# UI
import ipywidgets as widgets

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

def plots():
    # chart 1
    global slider_1
    # button to update chart
    button_1 = widgets.Button(description="Show/refresh chart")
    button_1.on_click(button_1_func)
    
    # vertical block
    window_1 = widgets.VBox([slider_1, button_1,])
       
    #tab_contents = ['Chart_1',]
    children = [window_1,]    
    accordion = widgets.Accordion(children=children)
    accordion.set_title(0, 'Chart_1')
    accordion.selected_index = 0
    display(accordion)
