# Hyperdiscog
## Create Spotify playlists with an artist's entire discography

### CLI Tool

You need a [Spotify developer app](https://developer.spotify.com/documentation/web-api/concepts/apps) to run this.

I will make a public web app, but Spotify takes forever to approve public usage of the API. 🤷🏽 Watch this space.

#### Environment Variables
```buildoutcfg env vars
export SPOTIPY_CLIENT_ID=<spotify_client_id>
export SPOTIPY_CLIENT_SECRET=<spotify_client_secret>
```

#### Install
```bash
 virtualenv venv
 source venv/bin/activate
 pip install -r requirements.txt
```

#### Run

```bash
python cli.py 
```

Edit `available_market = None` in spotify_client.py to your country code to only include tracks available to you
