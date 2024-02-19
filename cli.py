from clients.spotify_client import SpotifyClient


class PlaylistMaker:
    @classmethod
    def run(cls):
        spotify_client = SpotifyClient(auth_manager=SpotifyClient.get_local_auth_manager())
        artist_name = input("Enter artist name: ")
        artist_search_results = spotify_client.artist_search(artist_name)
        if len(artist_search_results) < 1:
            print(f"{artist_name} not found on Spotify")
            return
        elif len(artist_search_results) == 1:
            selected_artist = artist_search_results[0]
        else:
            select_artist_prompt = "Select artist:\n"
            for idx, artist_search_result in enumerate(artist_search_results):
                select_artist_prompt += f"{idx}   {artist_search_result['name']}   {artist_search_result['genres']}\n"
            selected_artist_idx = input(select_artist_prompt)
            selected_artist = artist_search_results[int(selected_artist_idx)]
        print(f"Creating discography playlist for {selected_artist['name']}...")
        playlist_id, playlist_url = spotify_client.make_playlist(selected_artist["id"], selected_artist["name"])
        print(f"Created playlist: {playlist_url}")


if __name__ == "__main__":
    PlaylistMaker.run()
