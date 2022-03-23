from common.youtube import channel_videos_list


url = "https://www.youtube.com/c/lexfridman"
videos = channel_videos_list(url)

print(videos)
