import os
from common.youtube import (
    channel_videos_list,
    download_media,
    extract_matching_chapters,
    split_media_chapters,
)


dir_path = os.getcwd()

url = input("Please enter YouTube Channel URL: ")
# Get a list of all videos from a YouTube channel
videos = channel_videos_list(url, "videos.csv")

# Provide keywords to look for
keywords = input("Please enter keywords to look for in video description."
                 "One word equals One keyword and they are whitespace delimited: ")
keywords = tuple(key for key in keywords.split(" "))

# Check against each video description for matching keywords
chapters = extract_matching_chapters(videos, keywords)

media_type = input("What media type would you like to download, 0 for Video, 1 for Audio: ")

# Download media based on matching keywords
download_media(chapters, dir_path, media_type=media_type)

# Split downloaded media into series of clips matching keywords
split_media_chapters(dir_path, chapters)
