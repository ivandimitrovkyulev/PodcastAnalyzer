import os
import subprocess
from os import path, listdir, getcwd, chdir, mkdir
from os.path import isfile, join
import re
import pandas as pd
from pytube import YouTube, Channel
from pprint import pprint
from multiprocessing.dummy import Pool
from common.helpers import extract_matching_chapters, download_media, channel_videos_list,split_media_chapters


dir_path = path.dirname(path.realpath(__file__)) + "/test"

keywords = ('bitcoin', 'cryptocurrency', 'money', 'inflation', 'ethereum', 'blockchain',
            'satoshi', 'nakamoto')
df_podcasts = pd.read_csv("LexFridman_Podcasts_Description.csv")


url_dict = extract_matching_chapters(df_podcasts, keywords)


split_media_chapters(dir_path, url_dict)
