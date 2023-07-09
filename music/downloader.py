from yt_dlp import YoutubeDL
import re
import string
import os
from .playlist_manager import Song
from unidecode import unidecode


def sanitize_filename(filename):
    # Decode the string to ASCII
    filename = unidecode(filename)

    # Create a whitelist of ASCII printable characters
    whitelist = set(string.ascii_letters + string.digits + '._-')

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Replace non-ASCII characters with underscores
    filename = ''.join([char if char in whitelist else '_' for char in filename])

    # Replace multiple consecutive underscores with a single underscore
    filename = re.sub('_+', '_', filename)

    filename = filename.rstrip('_')

    return filename


class MDownloader:

    def __init__(self):
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'restrictfilenames': True,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'default_search': 'auto',
        }

    def download(self, uid, uname, search_string):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(search_string, download=False)
                raw_title = info['entries'][0]['title']
                title = sanitize_filename(raw_title)

                filename = f"downloads/{title}.mp3"
                song_file = f"songs/{title}.json"

                # print("File Info: %s\n" % info['entries'][0])

                i0 = info['entries'][0]

                info_0 = {
                    "id": i0["id"],
                    "title": i0["title"],
                    "thumbnails": i0["thumbnails"],
                    "thumbnail": i0["thumbnail"],
                    "description": i0["description"],
                    "duration": i0["duration"],
                    "view_count": i0["view_count"],
                    "url": i0["original_url"],
                    "categories": i0["categories"],
                    "tags": i0["tags"],
                    "heatmap": i0["heatmap"],
                }

                # Check if the file exists before downloading it
                if not os.path.isfile(filename):
                    url = info['entries'][0]['webpage_url']
                    # YDL_OPTIONS['outtmpl'] = 'downloads/%(title)s.%(ext)s'  # Update output template
                    ydl.download([url])

                if os.path.isfile(song_file):
                    song = Song.from_json(song_file)
                    song.info = info_0
                    return song

                # TODO If the json file exists for the track then load that instead of making a new song.
            except Exception as e:
                print(e)
                # await ctx.send("Error: Song not found.")
                return None

            new_song = Song(title,
                            uid,
                            uname,
                            filename,
                            raw_title,
                            search_string,
                            0,
                            info_0)

            return new_song
