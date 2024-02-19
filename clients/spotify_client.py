import os
import spotipy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = os.getenv("HOST")
AUTH_SCOPE = "playlist-modify-private"
ADD_TO_PLAYLIST_BATCH_LIMIT = 100
GET_ALBUMS_BATCH_LIMIT = 20

# available_market = "ZA"  # TODO config
available_market = None


class SpotifyForbiddenException(Exception):
    pass


class SpotifyClient:
    def __init__(self, auth_manager=None, session=None):
        if not auth_manager and not session:
            raise Exception("Auth manager or session required")
        if not auth_manager:
            auth_manager = self.get_auth_manager_from_session(session)
        self.auth_manager = auth_manager
        self.spotify_client = spotipy.Spotify(auth_manager=auth_manager)

    @staticmethod
    def get_local_auth_manager():
        return spotipy.oauth2.SpotifyOAuth(
            redirect_uri="http://127.0.0.1:8080/",
            scope=AUTH_SCOPE
        )

    @staticmethod
    def get_auth_manager_from_session(session):
        return spotipy.oauth2.SpotifyOAuth(
            redirect_uri=f"{HOST}/",
            scope=AUTH_SCOPE,
            cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session),
        )

    def artist_search(self, artist_name):
        result = []
        search_params = {"q": f"artist:{artist_name}", "type": "artist", "limit": 50}
        search_result = self.spotify_client.search(**search_params)
        for item in search_result.get("artists", {}).get("items", []):
            result.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "genres": item.get("genres")
            })
        return result

    def make_playlist(self, artist_id, artist_name):
        albums = []
        album_type_counts = []
        for album_type in ['album', 'single', 'appears_on', 'compilation']:
            page = self.spotify_client.artist_albums(artist_id, limit=50, album_type=album_type)
            album_type_counts.append(page.get("total"))
            while page:
                albums.extend(page["items"])
                page = self.spotify_client.next(page)

        logger.info(f"{len(albums)}: {album_type_counts[0]} albums, "
                    f"{album_type_counts[1]} singles, {album_type_counts[2]} appearances, "
                    f"{album_type_counts[3]} compilations")

        albums = sorted(
            albums,
            key=lambda a: a["release_date"],
            reverse=False,
        )
        track_uris = []
        track_albums = {}
        album_results = self.batch_get_albums([album["id"] for album in albums])
        for album in album_results:
            album_artists = [a["name"].lower() for a in album["artists"]]
            for track in album["tracks"]["items"]:
                track_artists = [a["name"].lower() for a in track["artists"]]
                track_name = track["name"].lower()
                if artist_name.lower() in track_artists:
                    if not available_market or available_market.upper() in track["available_markets"]:
                        track_info = {"album": album["name"], "tracks_in_album": album["total_tracks"],
                                      "track_uri": track["uri"], "type": album["type"], "album_artists": album_artists,
                                      "track_artists": track_artists}
                        if track_albums.get(track_name):
                            track_albums[track_name].append(track_info)
                        else:
                            track_albums[track_name] = [track_info]
                        track_uris.append(track["uri"])

        exclude_tracks_uris = []

        for track, albums in track_albums.items():
            if len(albums) > 1:
                albums_by_artist = []
                other_albums = []
                for album in albums:
                    if artist_name.lower() in album["album_artists"]:
                        albums_by_artist.append(album)
                    else:
                        other_albums.append(album)

                if albums_by_artist:
                    albums = albums_by_artist
                    exclude_tracks_uris.extend([t["track_uri"] for t in other_albums])

                if len(albums) > 1:
                    exclude = sorted(albums, key=lambda a: a["tracks_in_album"], reverse=True)[1:]
                    exclude_tracks_uris.extend([t["track_uri"] for t in exclude])

        track_uris_to_add = [uri for uri in track_uris if uri not in exclude_tracks_uris]
        playlist_id, playlist_url = self.create_playlist(track_uris_to_add, artist_name)
        return playlist_id, playlist_url

    def create_playlist(self, track_uris_to_add: list, artist_name: str) -> (str, str):
        user = self.spotify_client.current_user()
        user_id = user["id"]
        playlist_name = f"{artist_name} discography"
        playlist = self.spotify_client.user_playlist_create(user_id, playlist_name, public=False, collaborative=False,
                                                            description=f"{artist_name}'s discography")
        playlist_url = playlist.get("external_urls", {}).get("spotify")
        playlist_id = playlist.get("id")
        self.batch_add_tracks_to_playlist(playlist_id, track_uris_to_add)
        return playlist_id, playlist_url

    def batch_get_albums(self, album_ids: list) -> list:
        if len(album_ids) > GET_ALBUMS_BATCH_LIMIT:
            batch = album_ids[:GET_ALBUMS_BATCH_LIMIT]
            queue = album_ids[GET_ALBUMS_BATCH_LIMIT:]
        else:
            batch = album_ids
            queue = None

        logger.info(f"Getting {len(batch)} albums...")
        result = self.spotify_client.albums(batch).get("albums")
        if queue:
            result += self.batch_get_albums(album_ids[GET_ALBUMS_BATCH_LIMIT:])
        return result

    def batch_add_tracks_to_playlist(self, playlist_id: str, track_data: list):
        if len(track_data) > ADD_TO_PLAYLIST_BATCH_LIMIT:
            batch = track_data[:ADD_TO_PLAYLIST_BATCH_LIMIT]
            queue = track_data[ADD_TO_PLAYLIST_BATCH_LIMIT:]
        else:
            batch = track_data
            queue = None

        logger.info(f"Adding {len(batch)} tracks to playlist...")
        self.spotify_client.playlist_add_items(playlist_id, batch)

        if queue:
            self.batch_add_tracks_to_playlist(playlist_id, track_data[ADD_TO_PLAYLIST_BATCH_LIMIT:])
