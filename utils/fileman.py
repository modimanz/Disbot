
import os
import fnmatch
import pickle
import random
import settings

#mp3_list = 'my_mp3.pkl'


#def save_mp3_list(mp3_files):
#    with open(settings.music_dir, 'wb') as file:
#        pickle.dump(mp3_files, file)


#def load_mp3_list():
#    with open(settings.music_dir, 'rb') as file:
#        my_mp3s = pickle.load(file)

#    return my_mp3s

def save_mp3_list(mp3_files):
    with open(os.path.join(settings.music_dir, 'song_list.pkl'), 'wb') as file:
        pickle.dump(mp3_files, file)


def load_mp3_list(music_dir = False):
    if not music_dir:
        music_dir = settings.music_dir

    pickle_file_path = os.path.join(music_dir, 'song_list.pkl')
    if not os.path.exists(pickle_file_path):
        return False
    else:
        with open(pickle_file_path, 'rb') as file:
            my_mp3s = pickle.load(file)

    return my_mp3s


# TODO open a random file from the music folder
def get_music_files(force_reload=False):

    if not force_reload:
        list_check = load_mp3_list()
        if list_check:
            return list_check

    music_dir = settings.music_dir

    mp3_files = []

    for root, dirs, files in os.walk(music_dir):
        for file in files:
            for ext in ['*.mp3', '*.wav', '*.mp4']:
                if fnmatch.fnmatch(file, ext):
                    mp3_files.append(os.path.join(root, file))

    save_mp3_list(mp3_files)
    return mp3_files


# TODO open a random file from the music folder
def get_random_music_files(music_dir, force_reload=False):

    if not force_reload:
        if os.path.exists(music_dir):
            return load_mp3_list()

    music_dir = music_dir

    mp3_files = []

    for root, dirs, files in os.walk(music_dir):
        for file in files:
            for ext in ['*.mp3', '*.wav', '*.mp4']:
                print("File: %s\n" % file)
                if fnmatch.fnmatch(file, ext):
                    mp3_files.append(os.path.join(root, file))

    save_mp3_list(mp3_files)
    return mp3_files


def get_random_music_file(music_dir, force_reload=False):
    files = get_random_music_files(music_dir, force_reload)
    return random.choice(files)

