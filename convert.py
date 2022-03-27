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
    query_keywords,
)


folder_path = os.getcwd() + "/audios"

# Pre-cleaned data set to exclude videos that are not podcasts
df = pd.read_csv('LexFridman_Podcasts_Description.csv')

# Provide keywords to look for
keywords = input("Please enter keywords to look for in video description.\n"
                 "Use commas for multiple keywords: ")
keywords = [key for key in re.split(r", |,", keywords)]

# Check against each video description for matching keywords
chapters = get_matching_chapters(df, keywords)

query_keywords(chapters, keywords)
proceed = input("Do you want to export media?: [y/n] ")
proceed = proceed.lower()

if proceed == "y":
    # Cut out chapters matching keywords
    split_media_chapters(folder_path, chapters)

    # Create image for each chapter with guest's description on as text
    list_image_info(folder_path)

    # Concat chapters and images of each episode
    concat_media_chapters_and_images(folder_path)

    # Final media file concatenation
    os.mkdir('Final')
    file_name = 'Final/' + "final_video.mp4"
    concat_media_demuxer(folder_path, out_filename=file_name)

    print(f"Final media saved in: {folder_path}/{file_name}")

else:
    print("Exiting.")
