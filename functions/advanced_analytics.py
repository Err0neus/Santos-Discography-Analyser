import pandas as pd
import matplotlib.pyplot as plt

def plotDivergingBars(df, x, y, green, red, sort_by_values = True):
    artist = df['ARTIST_NAME'][0]
    if sort_by_values == True:
        data = df.sort_values(by=[x])
    else:
        data = df.sort_values(by=[y], ascending = False)
    data = data[[y,x]]
    data['colors'] = [red if x < 0 else green for x in data[x]]
    plt.figure(figsize=(14,max(1.5, len(data[y].unique())/2)),
               dpi= 80)
           
    plt.hlines(y=data[y], xmin=0, xmax=data[x], color=data.colors, alpha=0.6, linewidth=15)
    plt.gca()
    plt.xlabel('Sentiment Score', fontsize=15)
    plt.ylabel('Track Title' if y == 'TRACK_TITLE' else 'Album', fontsize=15)
    plt.yticks(fontsize=12)
    plt.grid(linestyle='--', alpha=0.5)
    plt.show()