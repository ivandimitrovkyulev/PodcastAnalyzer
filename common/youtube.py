import os
import re
import subprocess
import pandas as pd

from tqdm import tqdm
from multiprocessing.dummy import Pool

from datetime import (
    timedelta,
    datetime
)
from pytube import (
    Channel,
    YouTube,
)
from common.resources import (
    list_files,
    most_common,
    get_chapters,
)


def channel_videos_list(
        channel_url: str,
        filename: str = "",
        write_to_file: bool = False,
) -> pd.DataFrame:
    """
    Given a YouTube channel URL, collects the info of all of its videos and constructs a DataFrame.

    :param channel_url: A URL of the YouTube channel
    :param filename: Name of the file to save to
    :param write_to_file: If True write to .csv file
    :returns: Pandas DataFrame with columns:
    Name, URL_Link, Length, Views, Publish_date, Description, Keywords, Author, ID
    """

    column_names = ('Name', 'URL_Link', 'Length', 'Views', "Publish_date", 'Description', 'Keywords', 'Author', 'ID')

    # Construct a YouTube channel object
    channel = Channel(channel_url)

    print(f"Collecting videos from - {channel.channel_name}, {channel_url}")

    if filename == "":
        name = re.sub(" ", "", channel.channel_name)
        filename = name + "_videos.csv"

    # Main info list
    videos_info = []

    for video in tqdm(channel.videos):

        time_stamp = str(timedelta(seconds=video.length))

        # Append video info to main list
        videos_info.append(
            [
                video.title,
                video.watch_url,
                time_stamp,
                video.views,
                video.publish_date,
                video.description,
                video.keywords,
                video.author,
                video.video_id,
            ]
        )

    # Construct a Pandas DataFrame and append to file
    df = pd.DataFrame(videos_info, columns=column_names)

    if write_to_file:
        df.to_csv(filename)

    return df


def download_media(
        chapter_dict: dict,
        pathname: str = "",
        media_type: int = 1,
) -> str:
    """
    Download media from YouTube given media URL list.

    :param chapter_dict: Dict of chapters of 'extract_matching_chapters' type
    :param pathname: Where to save. Default is current working dir.
    :param media_type: 0 for Video, 1 for Audio. Default 1-Audio
    :return: List of downloaded media
    """
    # list of all YouTube URLs
    url_list = [url for url in chapter_dict.keys()]
    # number of URLs
    media_num = len(url_list)

    media_names = [chapter_dict[chapter]['media_name'] for chapter in chapter_dict]

    args = zip(url_list, media_names)

    def download_audio(url_and_filename):
        url, filename = url_and_filename
        yt = YouTube(url)
        file = yt.streams.filter(only_audio=True).first().download(pathname,
                                                                   max_retries=2, filename=filename)

        return file

    def download_video(url_and_filename):
        url, filename = url_and_filename
        yt = YouTube(url)
        file = yt.streams.filter().get_highest_resolution().download(pathname,
                                                                     max_retries=2, filename=filename)

        return file

    try:
        os.chdir(pathname)
    except FileNotFoundError:
        os.mkdir(pathname)
        os.chdir(pathname)

    # If video selected
    if media_type == 0:
        print(f"{datetime.now()} - Started downloading video/s.")
        print(f"Downloading {media_num} items in total.")
        with Pool(os.cpu_count()) as pool:
            file_names = tqdm(pool.imap(download_video, args), total=media_num)
            media_list = [name for name in file_names]

    # If audio is selected
    else:
        print(f"{datetime.now()} - Started downloading audio/s.")
        print(f"Downloading {media_num} items in total.")
        with Pool(os.cpu_count()) as pool:
            file_names = tqdm(pool.imap(download_audio, args), total=media_num)
            media_list = [name for name in file_names]

    return f"{datetime.now()} - Downloaded:\n{media_list}"


def extract_matching_chapters(
        dataframe: pd.DataFrame,
        keywords: tuple = ("",),
) -> dict:
    """
    Extracts a dict with YouTube video chapters from a Pandas DataFrame object that match any of
    the keywords provided.

    :param dataframe: Pandas DataFrame of the 'channel_videos_list' return form
    :param keywords: List of string keywords to check against video chapters
    :returns: Dict of URLs with matching chapters
    """
    regex = re.compile(r"[^\w]+|[_]+")

    chapters_to_extract = {}
    for i, description in enumerate(dataframe['Description']):

        length = dataframe.at[i, 'Length']
        # Get a dict of video chapters
        video_chapters = get_chapters(description, length)

        chapters = {}
        for chapter in video_chapters.keys():
            # If any of the chapters matches at least one keyword
            for keyword in keywords:
                if keyword in chapter:
                    chapters[chapter] = video_chapters[chapter]
                    break

        # add to dict
        if len(chapters) > 0:
            url = dataframe.at[i, 'URL_Link']
            media_name = regex.sub("_", dataframe.at[i, 'Name'])

            chapters_to_extract[url] = {
                'media_name': media_name,
                'chapters': chapters,
            }

    return chapters_to_extract


def split_media_chapters(
        folder_path: str,
        chapter_dict: dict,
) -> list:
    """
    Given folder with media files, cuts out clips from each one based on dict of chapters
    with name, start & end timestamps.

    :param folder_path: Name of folder containing the media files
    :param chapter_dict: Dict of chapters of 'extract_matching_chapters' type
    :return: List of messages
    """

    regex = re.compile(r"[^\w]+|[_]+")

    def split_media(media, extension):
        media_name = media['media_name']

        filename = media_name + '.' + extension
        chapters = media['chapters']

        # Create new folder with video name
        os.mkdir(media_name)

        message = f"{media_name}\n"
        for chapter in chapters.keys():
            start = chapters[chapter][0]
            end = chapters[chapter][1]
            new_file = regex.sub("_", chapter) + "." + extension

            subprocess.run(['ffmpeg', '-i', f'{filename}', '-ss', f'{start}', '-to', f'{end}',
                           '-c:v', 'copy', '-c:a', 'copy', f'{media_name}/{new_file}'])

            message += f"{chapter}, {start}, {end}\n"

        command = f"""echo "{message}" > "{media_name}"/info.txt"""
        os.system(command)

        return message

    # cd into folder
    os.chdir(folder_path)

    # Get all video file names
    files = list_files(folder_path)

    assert len(files) > 0, f"{folder_path} contains no files."

    # Get most common file extension and use it as a base
    extensions = [file.split(".")[-1] for file in files]
    ext = most_common(extensions)

    args = [(media, ext) for media in chapter_dict.values()]

    with Pool(os.cpu_count()) as pool:
        results = pool.starmap(split_media, args)

        messages = [res for res in results]

    # cd back into main directory
    os.chdir("..")

    return messages
