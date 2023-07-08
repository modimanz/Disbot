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


class Song:
    def __init__(self, title, user_id, username, file_path, raw_title, search_string):
        self.title = title
        self.user_id = user_id
        self.username = username
        self.file_path = file_path
        self.raw_title = raw_title
        self.search_string = search_string
        self.play_count = 0

    def to_dict(self):
        return {
            'title': self.title,
            'user_id': self.user_id,
            'username': self.username,
            'file_path': self.file_path,
            'raw_title': self.raw_title,
            'search_string': self.search_string
        }

    def save(self, folder='songs'):
        # Create the songs folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Prepare filename
        filename = self.title.replace(" ", "_") + '.json'
        file_path = os.path.join(folder, filename)

        # Convert the song's data to a dictionary
        song_dict = {
            "title": self.title,
            "user_id": self.user_id,
            "username": self.username,
            "file_path": self.file_path,
            "raw_title": self.raw_title,
            "search_string": self.search_string
        }

        # Write the dictionary to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(song_dict, json_file)

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title'),
            user_id=data.get('user_id'),
            username=data.get('username'),
            file_path=data.get('file_path'),
            raw_title=data.get('raw_title'),
            search_string=data.get('search_string'),
        )


class Playlist:
    def __init__(self, name, creator_id, creator_username, songs):
        self.name = name
        self.creator_id = creator_id
        self.creator_username = creator_username
        self.songs = songs

    def add_song(self, song):
        self.songs.append(song)

    def remove_song(self, song_index):
        if song_index < len(self.songs):
            self.songs.pop(song_index)
        else:
            print("Invalid index")

    def to_dict(self):
        return {
            'name': self.name,
            'creator_id': self.creator_id,
            'creator_username': self.creator_username,
            'songs': [song.to_dict() for song in self.songs],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            creator_id=data.get('creator_id'),
            creator_username=data.get('creator_username'),
            songs=[Song.from_dict(song_data) for song_data in data.get('songs', [])],
        )


class PlaylistManager:
    def __init__(self):
        self.playlists_folder = 'playlists'
        os.makedirs(self.playlists_folder, exist_ok=True)  # Ensure the directory exists

    def create_playlist(self, name, creator_id, creator_username, song_list=[]):

        # Sanitize the playlist name and add ".json" suffix
        playlist_filename = re.sub(r'\W+', '', name) + '.json'
        new_playlist = Playlist(name, creator_id, creator_username, songs=song_list)

        with open(os.path.join(self.playlists_folder, playlist_filename), 'w') as f:
            json.dump(song_list, f)

    # def get_playlist(self, playlist_name):
    #    playlist_filename = re.sub(r'\W+', '', playlist_name) + '.json'
    #    with open(os.path.join(self.playlists_folder, playlist_filename), 'r') as f:
    #        song_list = json.load(f)
    #    return song_list

    # Saving playlist to a file
    def save_playlist(self, playlist):
        filepath = os.path.join(self.playlists_folder, playlist.name + '.json')
        with open(filepath, 'w') as f:
            json.dump(playlist.to_dict(), f)

    # Loading playlist from a file
    def load_playlist(self, name):
        filepath = os.path.join(self.playlists_folder, name + '.json')
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Playlist.from_dict(data)

    def list_playlists(playlists_dir='playlists'):
        playlist_names = []

        for file in os.listdir(playlists_dir):
            with open(os.path.join(playlists_dir, file), 'r') as f:
                playlist = json.load(f)
                playlist_names.append(playlist.get('name', 'No name'))

        return playlist_names

    def add_to_playlist(self, ctx, playlist_name, song):
        # TODO COMPLETE
        pass

    def remove_from_playlist(self, playlist_name, song_index):
        song_list = self.get_playlist(playlist_name)
        if 0 <= song_index < len(song_list):
            removed_song = song_list.pop(song_index)
            self.create_playlist(playlist_name, song_list)  # Overwrite the playlist file with the updated list
            return removed_song
        else:
            return None  # or raise an exception

