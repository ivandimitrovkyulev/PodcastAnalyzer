import os
import pandas as pd
from pprint import pprint
from common.youtube import (
    extract_matching_chapters,
    split_media_chapters,
    download_media,
)
from common.converter import (
    list_chapters_and_info,
    concat_media_demuxer,
    list_image_info,
    add_audio_to_video,
    concat_media_chapters_and_images,
)


folder_path = os.getcwd() + "/audios"

df = pd.read_csv('LexFridman_Podcasts_Description.csv')

keywords = ['meaning of life']
chapters = extract_matching_chapters(df, keywords)

split_media_chapters(folder_path, chapters)

list_image_info(folder_path)
concat_media_chapters_and_images(folder_path)

concat_media_demuxer(folder_path, out_filename="final_video.mp4")
