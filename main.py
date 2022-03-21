import os
import re
import pandas as pd
from pprint import pprint
import subprocess
from common.helpers import (
    extract_matching_chapters,
    download_media,
    split_media_chapters,
    list_chapters,
)


dir_path = os.path.dirname(os.path.realpath(__file__)) + "/videos"

keywords = ('bitcoin', 'ethereum', 'smart contract', 'money', 'inflation', 'satoshi',
            'cryptocurrency', 'satoshi', 'nakamoto', 'bank')

df = pd.read_csv("LexFridman_Podcasts_Description.csv")
chapters = extract_matching_chapters(df, keywords)
urls = [url for url in chapters.keys()]


concat_media(dir_path, 'media.txt', 'concat_video.mp4')
