# Project_Santos

<strong>Santos Lyrics Analyser</strong> is a Jupyter Notebook based interface downloading and visualizing music artists discography data, statistics and lyrics sentiment

## High level overview:

For any given musician/band name: <br>
   - retrieves the discography of studio albums, <br>
   - allows user to select albums from a list, then retrieves lyrics for songs on selected albums,<br>
   - collects data such as owners and album ratings from DISCOGS.COM, album and song placement in official Billboard music charts,<br>
   - performs lyrics sentiment analysis and generates scores, <br>
   - with a simple user interface, allows users to browse a number of visalisations (by user defined period intervals where applicable). 


<h3> Quick demo </h3>
<iframe width="560" height="315" src="https://www.youtube.com/embed/zorbor8p1Hc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

<h3> Example visualisations: </h3><br>
      • number of songs and albums over time [Example: David Bowie]<br><br><br> 
      
![image01](images/01_albums_and_songs_over_time.PNG)<br>
      • lexical diversity over time [Example: Eminem] <br> 
      • word clouds by album or period [Example: David Bowie] <br> 
      
![image03](images/03_wordclouds_bowie.PNG)<br>      
      • Discogs album ratings and statistics [Example: Depeche Mode]<br>
      
![image04](images/04_discogs_users__owners_and_average_ratings.png)<br>
![image05](images/05_average_discoggs_users_rating_by_album_vs_index.png)<br>
<br>
<br>
      • lurics sentiment scores across artist's discography [Example: Eminem]<br>
      • success of tracks and albums in Billboard charts over time<br>

![image07](images/songs_placement_in_billboard_100_charts.png)<br>
      • success in Billboard charts vs lyrics sentiment [Example: David Bowie] <br>
      
![image08](images/08_sentiment_vs_charts_bowie.PNG)<br>
      • lyrics sentiment over time [Example: David Bowie] <br>
      
![image09](images/09_sentiment_over_time_bowie.PNG)<br>
   

## Dependencies:

<h5><i>APIs and web scraping</i></h5>
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
