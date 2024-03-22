from googleapiclient.discovery import build
import pandas as pd
from flask import Flask, render_template, request

import ssl
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)


app = Flask(__name__)

# Set up your API key
api_key = 'AIzaSyAi59WP81vInKTCSjH-xqRXzknX-IcoOqk'

# Create a service object for interacting with the YouTube Data API
youtube = build('youtube', 'v3', developerKey=api_key)

#playList_id= 'UUNU_lfiiWBdtULKOw6X0Dig'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
def get_channel_stats():
    channel_id = request.form['message']
    if not channel_id :
        print("kindly provide a proper channel-Id")
        return render_template('index.html')
        
    print("channel-id:", channel_id)
    #channel_ids = get_channel_id(usernames)
    stats_data = get_channael_stats(youtube, channel_id)
    playList_id= stats_data [0]['channel_id']
    video_ids = get_video_ids(youtube, playList_id)
    all_video_data = get_video_details(youtube, video_ids)
    #all_video_data['Published']=pd.to_datetime(all_video_data['Published']).dt.date
    video_data_df = pd.DataFrame(all_video_data, columns=['Title', 'Published', 'Like_Count', 'View_Count'])
    video_data_df.sort_values(by='View_Count', ascending=False).head(10)

   
   
    return render_template('data.html', stats_data=stats_data, video_data_df=video_data_df)


'''
def get_channel_id(usernames):
    channel_ids = []
    for username in usernames:
        request = youtube.channels().list(
            part='id',
            forUsername=username
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            channel_id = response['items'][0]['id']
            channel_ids.append(channel_id)
    return channel_ids
'''

def get_channael_stats(youtube,channel_id):
    all_data = []
    request = youtube.channels().list(part='snippet,contentDetails,statistics', id= channel_id)
    response = request.execute()
    for i in range (len(response['items'])):
        data = dict(channel_name = response['items'][i]['snippet']['title'],
                subscriber = response['items'][i]['statistics']['subscriberCount'],
                Views = response['items'][i]['statistics']['viewCount'],
                Total_videos = response['items'][i]['statistics']['videoCount'],
                channel_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
        

    return all_data



def get_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50)
    response = request.execute()
    
    video_ids = []  

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
    next_Page_Token = response.get('nextPageToken')
    more_pages = True
    while more_pages:
        if next_Page_Token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_Page_Token)
            response = request.execute()
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_Page_Token = response.get('nextPageToken')
            
    return video_ids

def get_video_details(youtube, video_ids):
    all_video_data = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i+50]))
        response = request.execute()
        for j in response['items']:
            video_stat = {
                'Title': j['snippet']['title'],
                'Published': j['snippet']['publishedAt'],
                'Like_Count': j['statistics']['likeCount'],
                'View_Count': j['statistics']['viewCount']
            }
            all_video_data.append(video_stat)
    
    
    return all_video_data




if __name__ == '__main__':
    app.run(debug=True)
