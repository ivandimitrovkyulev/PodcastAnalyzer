import os
import re
import pandas as pd

from common.downloader import get_matching_chapters
from common.converter import (
    concat_media_chapters_and_images,
    concat_media_demuxer,
)
from common.info import (
    list_image_info,
    split_media_chapters,
)


folder_path = os.getcwd() + "/audios"

# Pre-cleaned data set to exclude videos that are not podcasts
df = pd.read_csv('LexFridman_Podcasts_Description.csv')

# Provide keywords to look for
keywords = input("Please enter keywords to look for in video description. "
                 "Use commas for multiple keywords: ")
keywords = [key for key in re.split(r", |,", keywords)]

# Check against each video description for matching keywords
chapters = get_matching_chapters(df, keywords)

# Cut out chapters matching keywords
split_media_chapters(folder_path, chapters)

# Create image for each chapter with guest's description on as text
list_image_info(folder_path)

# Concat chapters and images of each episode
concat_media_chapters_and_images(folder_path)

os.mkdir('Final')
# Final media file concatenation
concat_media_demuxer(folder_path, out_filename="Final/final_video.mp4")

print(f"Final media saved in: {folder_path}/Final/final_video.mp4")
