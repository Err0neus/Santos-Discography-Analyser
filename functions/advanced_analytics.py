import pandas as pd
import matplotlib.pyplot as plt

def plotDivergingBars(df, x, y, sort_by_values = True):
    artist = df['ARTIST_NAME'][0]
    if sort_by_values == True:
        data = df.sort_values(by=[x])
    else:
        data = df.sort_values(by=[y], ascending = False)
    data = data[[y,x]]
    data['colors'] = ['red' if x < 0 else 'green' for x in data[x]]
    plt.figure(figsize=(14,10), dpi= 80)
    
    # added instead of the plt.title to allow subtitle in different fonts
    plt.axes([.1,.1,.8,.7])
    # adapt chart title depending on what's being displayed
    plt.figtext(.5,.9,'Sentiment Analysis - diverging bars', fontsize=18, ha='center')
    if y == 'TRACK_TITLE':
        plt.figtext(.5,
                    .85,
                    'Artist: '
                    + artist
                    + " | Album: " 
                    + df['ALBUMS'].unique()[0]
                    + " | Year: "
                    + str(df['YEAR'].unique()[0]),
                    fontsize=15,ha='center')
    else:
        plt.figtext(.5,.85,'Artist: ' + artist ,fontsize=15,ha='center')
        
    plt.hlines(y=data[y], xmin=0, xmax=data[x], color=data.colors, alpha=0.6, linewidth=20)
    plt.gca()
    plt.xlabel('Sentiment Score', fontsize=15)
    plt.ylabel('Track Title' if y == 'TRACK_TITLE' else 'Album', fontsize=15)
    plt.yticks(fontsize=12)
    plt.grid(linestyle='--', alpha=0.5)
    plt.show()