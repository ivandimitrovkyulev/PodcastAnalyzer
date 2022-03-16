from os import path
from pytube import YouTube
from pprint import pprint
from .common.helpers import helpers


keywords = ('bitcoin', 'cryptocurrency', 'money', 'inflation', 'ethereum', 'blockchain',
            'satoshi', 'nakamoto')

df_podcasts = pd.read_csv("LexFridman_Podcasts_Description.csv")

# yt = YouTube("https://www.youtube.com/watch?v=nWTvXbQHwWs")
#a = yt.streams.filter(only_audio=True).first().download()

test = helpers.channel_videos_list()