import os
import re

from common.downloader import (
    channel_videos_list,
    download_media,
    get_matching_chapters,
)
from common.info import split_media_chapters

dir_path = os.getcwd()

url = input("Please enter YouTube Channel URL: ")
# Get a list of all videos from a YouTube channel
videos = channel_videos_list(url, "videos.csv")

# Provide keywords to look for
keywords = input("Please enter keywords to look for in video description."
                 "One word equals One keyword and they are whitespace delimited: ")
keywords = [key for key in re.split(r", |,", keywords)]

# Check against each video description for matching keywords
chapters = get_matching_chapters(videos, keywords)

media_type = int(input("What media type would you like to download, 0 for Video, 1 for Audio: "))

# Download media based on matching keywords
download_media(chapters, dir_path, media_type=media_type)

# Split downloaded media into series of clips matching keywords
split_media_chapters(dir_path, chapters)
