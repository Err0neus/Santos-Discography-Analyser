import pandas as pd
import matplotlib.pyplot as plt

def plotDivergingBars(df, x, y, green, red, sort_by_values = True):
    artist = df['ARTIST_NAME'][0]
    if sort_by_values == True:
        data = df.sort_values(by=[x])
    else:
        data = df.sort_values(by=[y], ascending = False)
    data = data[[y,x]]
    plt.figure(figsize=(14,max(1, len(data[y].unique())/2)),
               dpi= 80)
    # artificial vertical padding
    # make empty rows
    first_row_dict = {}
    first_row_dict[x] = [0]
    first_row_dict[y] = [' ']
    first_empty_row = pd.DataFrame.from_dict(first_row_dict)
    last_row_dict = {}
    last_row_dict[x] = [0]
    last_row_dict[y] = ['']
    last_empty_row = pd.DataFrame.from_dict(last_row_dict)
    # add empty rows to the dataframe
    data = first_empty_row.append(data.append(last_empty_row))
    # add colours    
    data['colors'] = [red if x < 0 else green for x in data[x]]
    # plot lines
    plt.hlines(y=data[y], xmin=0, xmax=data[x], color=data.colors, alpha=0.6, linewidth=15)
    #plt.gca()
    plt.xlabel('Sentiment Score', fontsize=15)
    plt.ylabel('Track Title' if y == 'TRACK_TITLE' else 'Album', fontsize=15)
    plt.yticks(fontsize=12)
    plt.grid(linestyle='--', alpha=0.5)
    plt.show()