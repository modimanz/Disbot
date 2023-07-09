import json
import os
import datetime
import time
import glob
import re

"""
TODO need to handle error cases, 
    such as what happens if a file doesn't exist, 
    or a playlist name is not found, etc.
    
    create corresponding Discord
"""


class Song:
    def __init__(self, title, user_id, username, file_path, raw_title, search_string, play_count=0, info=None):
        if info is None:
            info = {}
        self.title = title
        self.user_id = user_id
        self.username = username
        self.file_path = file_path
        self.raw_title = raw_title
        self.search_string = search_string
        self.play_count = play_count
        self.info = info

    def to_dict(self):
        return {
            'title': self.title,
            'user_id': self.user_id,
            'username': self.username,
            'file_path': self.file_path,
            'raw_title': self.raw_title,
            'search_string': self.search_string,
            'play_count': self.play_count,
            'info': self.info
        }

    def json_filename(self, folder="songs"):
        # Prepare filename
        filename = self.title.replace(" ", "_") + '.json'
        file_path = os.path.join(folder, filename)
        return file_path

    def save(self, folder='songs'):
        # Create the songs folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Prepare filename
        file_path = self.json_filename()
        # filename = self.title.replace(" ", "_") + '.json'
        # file_path = os.path.join(folder, filename)

        # Convert the song's data to a dictionary
        song_dict = {
            "title": self.title,
            "user_id": self.user_id,
            "username": self.username,
            "file_path": self.file_path,
            "raw_title": self.raw_title,
            "search_string": self.search_string,
            "play_count": self.play_count,
            "info": self.info,
        }

        # Write the dictionary to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(song_dict, json_file)

    def increment(self):
        self.play_count = self.play_count + 1
        self.save()

    @classmethod
    def from_json(cls, filepath):
        with open(filepath, 'r') as json_file:
            song_dict = json.load(json_file)

        song = Song(
            title=song_dict['title'],
            user_id=song_dict['user_id'],
            username=song_dict['username'],
            file_path=song_dict['file_path'],
            raw_title=song_dict['raw_title'],
            search_string=song_dict['search_string'],
            play_count=song_dict['play_count'],
            info=song_dict['info']
        )

        return song

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title'),
            user_id=data.get('user_id'),
            username=data.get('username'),
            file_path=data.get('file_path'),
            raw_title=data.get('raw_title'),
            search_string=data.get('search_string'),
            play_count=data.get('playcount'),
            info=data.get('info'),
        )


class Playlist:
    def __init__(self, name, creator_id, creator_username, songs):
        self.name = name
        self.creator_id = creator_id
        self.creator_username = creator_username
        self.songs = songs
        self.last_loaded = 0.0

    def add_song(self, song, playlist_folder):
        self.songs.append(song)
        self.save(playlist_folder)

    def remove_song(self, song_index):
        if song_index < len(self.songs):
            self.songs.pop(song_index)
        else:
            print("Invalid index")

    def save(self, playlist_folder):
        try:
            filepath = os.path.join(playlist_folder, self.name + '.json')
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f)
            print(f"Playlist {self.name} has been saved successfully.")
        except Exception as e:
            print(e)
            print("Error saving playlist:\n")

    @classmethod
    def load(cls, filepath):
        # Load the JSON data from the file
        with open(filepath, 'r') as json_file:
            playlist_dict = json.load(json_file)

            # Convert each song dictionary to a Song object
            # songs = [Song(song_dict['title'], song_dict['user_id'], song_dict['username'], song_dict['file_path'],
            #              song_dict['raw_title'], song_dict['search_string']) for song_dict in playlist_dict['songs']]

            songs = [Song.from_json(song_path) for song_path in playlist_dict['songs']]

            # Create a new instance of Playlist using the dictionary
            playlist = Playlist(
                name=playlist_dict['name'],
                creator_id=playlist_dict['creator_id'],
                creator_username=playlist_dict['creator_username'],
                songs=songs,
            )
            playlist.last_loaded = time.time()

        return playlist

    def to_dict(self):

        songs = [song.json_filename() for song in self.songs]
        return {
            'name': self.name,
            'creator_id': self.creator_id,
            'creator_username': self.creator_username,
            'songs': songs,
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
        self.playlists = []
        self.load_all_playlists()
        self.shuffle = {}
        self.repeat = {}

    def is_repeat(self, guild_id):

        if (guild_id in self.repeat
                and self.repeat[guild_id] is True):
            return True
        else:
            return False

    def is_shuffle(self, guild_id):
        if (guild_id in self.shuffle
                and self.shuffle[guild_id] is True):
            return True
        else:
            return False

    def create_playlist(self, name, creator_id, creator_username, song_list=[]):

        # Sanitize the playlist name and add ".json" suffix
        # playlist_filename = re.sub(r'\W+', '', name) + '.json'
        new_playlist = Playlist(name, creator_id, creator_username, songs=song_list)

        self.save_playlist(new_playlist)
        # with open(os.path.join(self.playlists_folder, playlist_filename), 'w') as f:
        #    json.dump(song_list, f)

    # def get_playlist(self, playlist_name):
    #    playlist_filename = re.sub(r'\W+', '', playlist_name) + '.json'
    #    with open(os.path.join(self.playlists_folder, playlist_filename), 'r') as f:
    #        song_list = json.load(f)
    #    return song_list

    # Saving playlist to a file
    def save_playlist(self, playlist):
        # Add the playlist to global playlists list if it does not exist
        if playlist not in self.playlists:
            self.playlists.append(playlist)

        playlist.save(self.playlists_folder)

    def prune_playlists(self):
        """
        This function prunes the loaded playlists if their files don't exist anymore.
        """

        directory = self.playlists_folder

        # Get a list of all .json files in the directory
        existing_files = [f for f in os.listdir(directory) if f.endswith('.json')]

        # Remove the .json extension from the filenames
        existing_files = [os.path.splitext(f)[0] for f in existing_files]

        # Create a new list of playlists where their name matches a filename
        playlists = [playlist for playlist in self.playlists if playlist.name in existing_files]

        return playlists

    # Loading playlist from a file by name of playlist
    def load_playlist(self, name):
        # Load the playlist file
        filepath = os.path.join(self.playlists_folder, name + '.json')

        # If the file does not exist, return None or handle the error as you see fit
        if not os.path.exists(filepath):
            print(f"No playlist found with the name: {name}")
            return None

        # Find the playlist in the global list
        for playlist in self.playlists:
            if playlist.name == name:
                print("Found playlist %s\n" % name)
                # Get the last modified time of the playlist file
                file_mod_time = os.path.getmtime(filepath)
                # Check if the file has been modified since the last load
                if file_mod_time > playlist.last_loaded:
                    # If the file is newer, reload it
                    playlist = Playlist.load(filepath)
                    # with open(filepath, 'r') as f:
                    #    playlist_dict = json.load(f)
                    # playlist.load_from_dict(playlist_dict)
                    # playlist.last_loaded = file_mod_time
                return playlist

        # If the playlist was not found in the global list, load it from the file
        playlist = Playlist.load(filepath)

        # Add the newly loaded playlist to the global list
        self.playlists.append(playlist)

        return playlist

    def delete_playlist(self, name, directory="playlists"):
        """
        This function deletes a playlist file.
        """
        # Add the .json extension
        name += ".json"

        # Check if the file exists
        if os.path.exists(os.path.join(directory, name)):
            # Delete the file
            os.remove(os.path.join(directory, name))
            print(f"Deleted playlist: {name}")
        else:
            print("The playlist does not exist.")
        self.load_all_playlists()

    def list_playlists(self, playlists_dir='playlists'):
        if self.playlists is None or len(self.playlists) < 1:
            return

        playlist_names = []

        for file in os.listdir(playlists_dir):
            with open(os.path.join(playlists_dir, file), 'r') as f:
                playlist = json.load(f)
                playlist_names.append(playlist.get('name', 'No name'))

        return playlist_names

    @staticmethod
    def last_modified(filepath):
        t = os.path.getmtime(filepath)
        return datetime.datetime.fromtimestamp(t)

    def load_all_playlists(self):
        # Get all files in directory
        files = os.listdir(self.playlists_folder)

        # Filter out non-JSON files
        files = [f for f in files if f.endswith('.json')]

        # For each JSON file, load the playlist
        for file in files:
            file_path = os.path.join(self.playlists_folder, file)

            last_modified = self.last_modified(file_path)

            for playlist in self.playlists:
                if playlist.name == os.path.splitext(file) and playlist.last_loaded > last_modified:
                    continue
            else:

                playlist = Playlist.load(file_path)
                self.playlists.append(playlist)
        self.prune_playlists()

    def add_to_playlist(self, ctx, playlist_name, song):
        """
        Add song to playlist

        :param ctx:
        :param playlist_name:
        :param song:
        :return:
        """
        playlist = self.load_playlist(playlist_name)
        playlist.add_song(song, self.playlists_folder)

    def remove_from_playlist(self, playlist_name, song_index):

        playlist = self.load_playlist(playlist_name).songs
        song_list = playlist.songs
        if 0 <= song_index < len(song_list):
            removed_song = song_list.pop(song_index)
            playlist.songs = song_list
            playlist.save()
            self.load_all_playlists()
            # _ (playlist_name, song_list)  # Overwrite the playlist file with the updated list
            return removed_song
        else:
            return None  # or raise an exception
