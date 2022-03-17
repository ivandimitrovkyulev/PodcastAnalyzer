import os
import re
import pandas as pd
from pytube import YouTube, Channel
from pprint import pprint
from common.helpers import extract_chapters, download_audio


dir_path = os.path.dirname(os.path.realpath(__file__)) + "/videos"

keywords = ('bitcoin', 'cryptocurrency', 'money', 'inflation', 'ethereum', 'blockchain',
            'satoshi', 'nakamoto')

df_podcasts = pd.read_csv("LexFridman_Podcasts_Description.csv")

url_dict = extract_chapters(df_podcasts, keywords)
download_audio(url_dict, dir_path)
