from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
from flask import Flask, render_template


app = Flask(__name__)

# Set up your API key
api_key = 'AIzaSyAi59WP81vInKTCSjH-xqRXzknX-IcoOqk'

# Create a service object for interacting with the API
youtube = build('youtube', 'v3', developerKey=api_key)

@app.route('/')
def home():
    return render_template('index.html')



@app.route('/data', methods=['GET', 'POST'])
def index():
    username = ['krishnaik06']
    channel_id = get_channael_id(username)
    stats_data = get_channael_stats(youtube,channel_id)
    stats_data = pd.DataFrame(stats_data)
    return f"Channel IDs: {stats_data}"

def get_channael_id(username):
    

    channel_ids = []
# Make a request to the API
    for i in username :
        request = youtube.channels().list(
            part='id',
            forUsername=i
        )
        response = request.execute()
        #print(response)
        if 'items' in response and len(response['items']) > 0:
            channel_id = response['items'][0]['id']
            #print(channel_id)
            channel_ids.append(channel_id)

    return channel_ids

def get_channael_stats(yt,channel_id):
    all_data = []
    request = yt.channels().list(part='snippet,contentDetails,statistics', id= channel_id)
    response = request.execute()
    for i in range (len(response['items'])):
        data = dict(channel_name = response['items'][i]['snippet']['title'],
                subscriber = response['items'][i]['statistics']['subscriberCount'],
                Views = response['items'][i]['statistics']['viewCount'],
                Total_videos = response['items'][i]['statistics']['videoCount'],
                channel_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
    return all_data

def get_video_ids(yt,playlist_id):
    request = yt.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50)
    response = request.execute()
    
    video_ids = []  

    for i in range (len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
    next_Page_Token=response.get('nextPageToken')
    more_pages = True
    while more_pages :
        if next_Page_Token is None:
            more_pages = False
        else:
            request = yt.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_Page_Token)
            response = request.execute()
            for i in range (len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_Page_Token=response.get('nextPageToken')
            
   
            
    return render_template('data.html')




if __name__ == '__main__':
    print ("Starting")
    app.run(debug=True)