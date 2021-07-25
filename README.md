# Project_Santos

<b><u>Santos Lyrics Analyser</b></u> is a Jupyter Notebook based interface downloading and visualizing music artists discography data, statistics and lyrics sentiment

## High level overview:

For any given musician/band name: <br>
   - retrieves the discography of studio albums, <br>
   - allows user to select albums from a list, then gets lyrics for each song on selected albums,<br>
   - collects data such as owners and album ratings from DISCOGS.COM, album and song placement in official Billboard music charts,<br>
   - performs lyrics sentiment analysis and generates scores, <br>
   - with a simple user interface, allows users to browse a number of visalisations (by user defined period intervals where applicable). 
   
<h3> Example visualisations: </h3><br>
      • number of songs and albums over time<br><br><br> 
      • word clouds by album or period <br> 
      • lexical diversity over time <br> --eminem
      • Discogs album ratings and statistics [Artist: Depeche Mode]<br>
      ![image](https://user-images.githubusercontent.com/43116506/126905328-0a472b37-d208-4f42-b277-18084147eb46.png)<br>
      ![image](https://user-images.githubusercontent.com/43116506/126905394-66a6056b-01f3-4470-a6b3-5c24518419e9.png)
<br>
<br>
      • success of tracks and albums in Billboard charts over time<br>
      ![image](https://user-images.githubusercontent.com/43116506/126905506-f3b84444-6621-459c-b96c-9d2e41671d84.png)<br>
      • lyrics sentiment over time <br>
      • success in Billboard charts vs lyrics sentiment <br>
   

## Dependencies:

<h5><i>APIs</i></h5>
lyricsgenius<br>
lxml.html<br>
cssselect<br>
discogs_client<br>
requests<br>
lyricsmaster<br>

<h5><u><i>data processing and charts</i></u></h5>
matplotlib<br>
pandas<br>
numpy<br>
time<br>
seaborn<br>
fuzzy_pandas<br>
chord<br>

<h5><u><i>UI</i></u></h5>
ipywidgets<br>
IPython<br>
tqdm<br>

<h5><u><i>word processing</i></u></h5>
re<br>
os<br>
nltk<br>
string<br>
wordcloud<br>
