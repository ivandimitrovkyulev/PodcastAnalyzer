from pytube import YouTube


url = "https://www.youtube.com/watch?v=DbXjoXnIxQo&t=2732s"
yt = YouTube(url)

captions = yt.captions.

print(captions)