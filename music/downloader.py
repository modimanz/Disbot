from yt_dlp import YoutubeDL
import re
import os


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

    def download(self, search_string):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(search_string, download=False)
                raw_title = info['entries'][0]['title']
                title = re.sub('[^a-zA-Z0-9\-_ .`\'|/]', '', raw_title)  # Remove special characters
                title = title.replace(" ", "_")
                title = title.replace("`", "_")
                title = title.replace("'", "_")
                title = title.replace("|", "_")
                title = title.replace("/", "_")
                title = re.sub('_+', '_', title)
                filename = f"downloads/{title}.mp3"

                # print("File Info: %s\n" % info['entries'][0])

                # Check if the file exists before downloading it
                if not os.path.isfile(filename):
                    url = info['entries'][0]['webpage_url']
                    # YDL_OPTIONS['outtmpl'] = 'downloads/%(title)s.%(ext)s'  # Update output template
                    ydl.download([url])
            except Exception as e:
                print(e)
                # await ctx.send("Error: Song not found.")
                return False, False, False

            return raw_title, title, filename
