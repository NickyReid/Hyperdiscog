# Hyperdiscog
## Create Spotify playlists with an artist's entire discography

- Removes duplicates when tracks are featured on multiple albums/singles
- Adds tracks that feature on other artists' albums or compilations

Create an app on the [Spotify For Developers](https://developer.spotify.com/documentation/web-api/concepts/apps) site to get a client ID and client secret. 


### CLI Tool

#### Environment Variables
```buildoutcfg env vars
export SPOTIPY_CLIENT_ID=<spotify client id>
export SPOTIPY_CLIENT_SECRET=<spotify client secret>
```

#### Install
```bash
 virtualenv venv
 source venv/bin/activate
 pip install spotipy==2.23.0
```

#### Run

```bash
python cli.py 
```

### Web App

Add `http://0.0.0.0:8080/` to the Redirect URIs in your [Spotify app settings](https://developer.spotify.com/dashboard)


#### Environment Variables
```buildoutcfg env vars
export HOST=http://0.0.0.0:8080
export SPOTIPY_CLIENT_ID=<spotify client id>
export SPOTIPY_CLIENT_SECRET=<spotify client secret>
export SESSION_SECRET_KEY=<session secret key>
```

#### Install
```bash
 virtualenv venv
 source venv/bin/activate
 pip install  -r requirements.txt
```

#### Run

```bash
gunicorn app:app --bind 0.0.0.0:8080 
```
