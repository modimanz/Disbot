import json
import os
import glob
import re

"""
TODO need to handle error cases, 
    such as what happens if a file doesn't exist, 
    or a playlist name is not found, etc.
    
    create corresponding Discord
"""


class PlaylistManager:
    def __init__(self):
        self.playlists_folder = 'playlists'
        os.makedirs(self.playlists_folder, exist_ok=True)  # Ensure the directory exists

    def create_playlist(self, playlist_name, song_list):
        # Sanitize the playlist name and add ".json" suffix
        playlist_filename = re.sub(r'\W+', '', playlist_name) + '.json'
        with open(os.path.join(self.playlists_folder, playlist_filename), 'w') as f:
            json.dump(song_list, f)

    def get_playlist(self, playlist_name):
        playlist_filename = re.sub(r'\W+', '', playlist_name) + '.json'
        with open(os.path.join(self.playlists_folder, playlist_filename), 'r') as f:
            song_list = json.load(f)
        return song_list

    def list_playlists(self):
        return [os.path.basename(x) for x in glob.glob(f'{self.playlists_folder}/*.json')]

    def remove_from_playlist(self, playlist_name, song_index):
        song_list = self.get_playlist(playlist_name)
        if 0 <= song_index < len(song_list):
            removed_song = song_list.pop(song_index)
            self.create_playlist(playlist_name, song_list)  # Overwrite the playlist file with the updated list
            return removed_song
        else:
            return None  # or raise an exception

