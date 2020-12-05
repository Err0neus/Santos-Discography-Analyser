# Project_Santos

## High level overview:

For any given musician/band name: <br>
   - gets the discography of studio albums, <br>
   - allows user to select albums from a list, then gets lyrics for each song on selected albums,<br>
   - gathers album ratings from Discogs website, album and song placement in Billboard charts,<br>
   - performs lyrics sentiment analysis and generates scores, <br>
   - with a simple user interface, allows users to browse through visalisations of (by user defined period intervals where applicable: <br>
      • number of songs and albums over time<br>
      • word clouds by album or period <br>
      • lexical diversity over time <br>
      • Discogs album ratings and statistics <br> 
      • success of tracks and albums in Billboard charts over time<br>
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
