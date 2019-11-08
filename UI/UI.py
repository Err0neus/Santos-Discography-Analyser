import matplotlib.pyplot as plt
import pandas as pd
import time
from matplotlib.ticker import MaxNLocator


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
    
    fig, ax1 = plt.subplots(figsize=(11,7))

    color = 'tab:red'
    ax1.set_xlabel('period')
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
    
    
# UI
import ipywidgets as widgets

def plot_by_period():
    
    period_size_selector = widgets.IntSlider(
        value=1,
        min=1,
        max=10,
        step=1,
        description='Period (# of years)',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='d'
    )


