import os
import logging

from clients.spotify_client import SpotifyClient
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.secret_key = os.getenv("SESSION_SECRET_KEY")


@app.route("/", methods=["POST", "GET"])
def index():
    step = 1
    msg = None
    auth_url = None
    artist_search_results = None
    artist_albums = None
    playlist_url = None
    selected_artist_name = None
    search_artist = None

    try:
        def _get_artist_albums(_selected_artist_id):
            return SpotifyClient(session=session).get_album_summaries_for_artist(_selected_artist_id)

        # TODO get state from query params instead of session
        if "step" in session:
            step = session["step"]
        if "artist_albums" in session:
            artist_albums = session["artist_albums"]
        if "selected_artist_name" in session:
            selected_artist_name = session["selected_artist_name"]

        if not artist_albums:
            step = 2
        if "access_token" not in session:
            step = 1

        if step == 1:
            spotify_auth_manager = SpotifyClient.get_auth_manager_from_session(session)
            auth_url = spotify_auth_manager.get_authorize_url()

        if request.method == "GET":
            spotify_auth_code = request.args.get("code")
            if spotify_auth_code:
                spotify_auth_manager = SpotifyClient.get_auth_manager_from_session(session)
                session["access_token"] = spotify_auth_manager.get_access_token(
                    spotify_auth_code, as_dict=False
                )
                step = 2
                session["step"] = step
                return redirect("/")

        elif request.method == "POST":
            search_artist = request.form.get("search_artist")
            selected_artist_id = request.form.get("selected_artist_id")
            if request.form.get("selected_artist_name"):
                selected_artist_name = session["selected_artist_name"] = request.form.get("selected_artist_name")
            albums_selection = request.form.get("albums_selection")
            if search_artist:
                logger.info(f"Searching for {search_artist}")
                spotify_client = SpotifyClient(session=session)
                artist_search_results = spotify_client.artist_search(search_artist)

                if len(artist_search_results) < 1:
                    logger.info(f"{search_artist} not found on Spotify")
                    step = 2
                    msg = f"Couldn't find '{search_artist}'"

                elif len(artist_search_results) == 1:
                    step = 5
                    session["step"] = step
                    selected_artist = artist_search_results[0]
                    session["selected_artist_name"] = selected_artist["name"]
                    artist_albums = _get_artist_albums(selected_artist['id'])
                else:
                    step = 3
                    session["step"] = step
            elif selected_artist_id:
                step = 5
                session["step"] = step
                artist_albums = _get_artist_albums(selected_artist_id)
            elif albums_selection:
                selected_album_ids = []
                for k, _ in request.form.items():
                    if "album_id" in k.lower():
                        selected_album_ids.append(k.split("album_id_")[1])
                remove_duplicates = bool(request.form.get("remove_duplicates"))
                remove_duplicates_favour = request.form.get("remove_duplicates_favour")
                album_order = request.form.get("album_order")

                spotify_client = SpotifyClient(session=session)

                playlist_id, playlist_url = spotify_client.make_playlist(selected_album_ids, selected_artist_name,
                                                                         album_order=album_order,
                                                                         remove_duplicates=remove_duplicates,
                                                                         remove_duplicates_favour=remove_duplicates_favour)
                step = 6
    except Exception:
        logger.exception(f"Unhandled exception")
        msg = "Something went wrong"
        session.clear()

    return render_template(
        "index.html",
        step=step,
        auth_url=auth_url,
        artist_search_results=artist_search_results,
        artist_albums=artist_albums,
        playlist_url=playlist_url,
        msg=msg,
        search_artist=search_artist,
    )
