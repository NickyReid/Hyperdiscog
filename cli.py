import argparse
from clients.spotify_client import SpotifyClient


class PlaylistMaker:
    @classmethod
    def run(cls):

        remove_duplicates = True
        remove_duplicates_favour = "length"
        album_order = "asc"

        parser = argparse.ArgumentParser()
        parser.add_argument("--remove_duplicates", help="remove duplicate tracks from playlist",
                            type=bool, default=remove_duplicates)
        parser.add_argument("--album_order", help="album release order. "
                                                  "'asc' for oldest first, 'desc' for newest first",
                            default=album_order)
        parser.add_argument("--remove_duplicates_favour", help="Which tracks to keep when removing duplicates. "
                                                               "can be 'old', 'new' or 'length'",
                            default=remove_duplicates_favour)
        args = parser.parse_args()

        if args.remove_duplicates is not None:
            remove_duplicates = bool(args.remove_duplicates)
        if args.remove_duplicates_favour:
            if args.remove_duplicates_favour not in ["new", "old", "length"]:
                raise ValueError("remove_duplicates_favour must be one of ['new,' 'old', 'length']")
            remove_duplicates_favour = args.remove_duplicates_favour
        if args.album_order:
            if args.album_order not in ["asc", "desc"]:
                raise ValueError("album_order must be one of ['asc,' 'desc']")
            album_order = args.album_order

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
        print(f"Remove duplicates:{remove_duplicates}; remove_duplicates_favour:{remove_duplicates_favour}: "
              f"album_order:{album_order}")
        album_ids = spotify_client.get_album_ids_for_artist(selected_artist["id"])
        playlist_id, playlist_url = spotify_client.make_playlist(album_ids=album_ids,
                                                                 artist_name=selected_artist["name"],
                                                                 remove_duplicates=remove_duplicates,
                                                                 remove_duplicates_favour=remove_duplicates_favour,
                                                                 album_order=album_order)
        print(f"Created playlist: {playlist_url}")


if __name__ == "__main__":
    PlaylistMaker.run()
