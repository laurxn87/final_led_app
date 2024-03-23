from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import serial 

# Authenticate with Spotify using the Client Credentials flow
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

username = os.getenv("SPOTIPY_CLIENT_USERNAME")
scope = 'user-read-playback-state'
token = spotipy.util.prompt_for_user_token(username, scope)
if token:
    print("Got token for", username)
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

app = Flask(__name__)

messages = []

# check arduino is available 
arduino = None
if os.path.exists('/dev/cu.usbmodem14201'):
    arduino = serial.Serial('/dev/cu.usbmodem14201', 9600)


@app.route('/')
def index():
    results = sp.current_user_playing_track()
    if results:
        track = results['item']
        trackname = track['name']
        artist = track['artists'][0]['name']

        if arduino:
            arduino.write(b'1') # send 1 to arduino

        return render_template('index.html', trackname=trackname, artist=artist)
    else:
        print("yikes")
        return render_template('index.html')

@app.route('/check', methods=['GET', 'POST'])
def check():
    results = sp.current_user_playing_track()
    if results:
        track = results['item']
        trackname = track['name']
        artist = track['artists'][0]['name']
        return jsonify({'trackname': trackname, 'artist': artist})
    else:
        return jsonify({'trackname': None, 'artist': None})    

@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        search = request.form['search']
        # Search for the track
        if not search:
            print('no search term')
            flash('Please enter a track name')
        else:
            print('searching for:', search)
            results = sp.search(q='track:' + search, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                print('track:', track)
                return render_template('search.html', track=track)
            
            else:
                messages.append('No results found')
                flash('No results found')
                return redirect(url_for('index'))

    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
