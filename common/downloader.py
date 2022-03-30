import os
import re
import pandas as pd

from functools import wraps
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
from common.info import get_chapters

from common.variables import (
    column_names,
    regex_non_word,
)


def channel_videos_list(
        channel_url: str,
        filename: str = "",
) -> pd.DataFrame:
    """
    Given a YouTube channel URL, collects the info of all of its videos and constructs a DataFrame.

    :param channel_url: A URL of the YouTube channel
    :param filename: Name of the file to save to. If not provided will only return DataFrame
    :returns: Pandas DataFrame with columns:
    Name, URL_Link, Length, Views, Publish_date, Description, Keywords, Author, ID
    """

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

    if filename != "":
        df.to_csv(filename)

    return df


def download_media(
        chapter_dict: dict,
        pathname: str = None,
        media_type: int = 1,
) -> str:
    """
    Download media from YouTube given a URL list.

    :param chapter_dict: Dict of chapters of 'get_matching_chapters' type
    :param pathname: Where to save. Default is current working dir.
    :param media_type: 0 for Video, 1 for Audio. Default 1-Audio
    :return: List of downloaded media
    """
    def error_handler_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                value = func(*args, **kwargs)

                return value
            except Exception:
                print(f"Something went wrong while downloading: {args[0]}. File now saved.")

        return wrapper

    if pathname is None:
        pathname = os.getcwd()

    # list of all YouTube URLs
    url_list = [url for url in chapter_dict.keys()]
    # number of URLs
    media_num = len(url_list)

    media_names = [chapter_dict[chapter]['media_name'] for chapter in chapter_dict]

    arguments = zip(url_list, media_names)

    @error_handler_wrapper
    def download_audio(url_and_filename):
        url, filename = url_and_filename
        yt = YouTube(url)
        extension = yt.streams.filter(only_audio=True).first().mime_type
        filename += "." + extension.split("/")[-1]
        file = yt.streams.filter(only_audio=True).first().download(pathname,
                                                                   max_retries=2, filename=filename)

        return file

    @error_handler_wrapper
    def download_video(url_and_filename):
        url, filename = url_and_filename
        yt = YouTube(url)
        extension = yt.streams.filter().get_highest_resolution().mime_type
        filename += "." + extension.split("/")[-1]
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
        print(f"Downloading {media_num} item/s in {pathname}")

        with Pool(os.cpu_count()) as pool:
            file_names = tqdm(pool.imap(download_video, arguments), total=media_num)
            media_list = [name for name in file_names]

    # If audio is selected
    else:
        print(f"{datetime.now()} - Started downloading audio/s.")
        print(f"Downloading {media_num} item/s in {pathname}")

        with Pool(os.cpu_count()) as pool:
            file_names = tqdm(pool.imap(download_audio, arguments), total=media_num)
            media_list = [name for name in file_names]

    return f"{datetime.now()} - Downloaded:\n{media_list}"


def get_matching_chapters(
        dataframe: pd.DataFrame,
        keywords: list = None,
) -> dict:
    """
    Extracts a dict of YouTube video chapters, from a Pandas DataFrame object, that match any of
    the keywords provided.

    :param dataframe: Pandas DataFrame of the 'channel_videos_list' return form
    :param keywords: List of string keywords to check against video chapters
    :returns: Dict of URLs with matching chapters
    """
    if keywords is None:
        keywords = [""]

    chapters_to_extract = {}
    for i, description in enumerate(dataframe['Description']):

        length = dataframe.at[i, 'Length']
        # Get a dict of video chapters
        video_chapters = get_chapters(description, length)

        chapters = {}
        for chapter in video_chapters.keys():
            # Split chapter into words
            chapter_words = regex_non_word.split(chapter)
            # If any of the chapters matches at least one keyword
            for keyword in keywords:
                try:
                    sign = keyword[0]
                except IndexError:
                    sign = ""

                if sign == "-":
                    word = keyword[1:].lower()
                else:
                    word = keyword.lower()

                if word in chapter_words and sign == "-":
                    break

                if word in chapter_words and sign != "-":
                    # Add chapter to dict
                    chapters[chapter] = video_chapters[chapter]
                    break

            # If a negated keyword matches and already added, delete from chapters
            for keyword in keywords:
                try:
                    sign = keyword[0]
                except IndexError:
                    sign = ""

                if sign == "-":
                    word = keyword[1:].lower()
                else:
                    word = keyword.lower()

                if word in chapter_words and sign == "-":
                    try:
                        del chapters[chapter]
                    except KeyError:
                        pass

        # add to dict
        if len(chapters) > 0:
            url = dataframe.at[i, 'URL_Link']
            media_name = regex_non_word.sub("_", dataframe.at[i, 'Name'])
            guest = dataframe.at[i, 'Description'].split(".")[0]

            chapters_to_extract[url] = {
                'media_name': media_name,
                'guest': guest,
                'chapters': chapters,
            }

    return chapters_to_extract
