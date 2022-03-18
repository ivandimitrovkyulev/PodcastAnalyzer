import os
import re
import subprocess
import pandas as pd
from datetime import timedelta
from multiprocessing.dummy import Pool
from pytube import (
    Channel,
    YouTube,
)


def get_chapters(
        description: str,
        video_length: str,
) -> dict:
    """
    Attempt to extract YouTube video chapters from its description.

    :param description: String to iterate through and look for chapters
    :param video_length: Video length in the %H:%M:%S format as last timestamp
    :returns: Dict with chapters containing name, start time & end time
    """

    # Regex to match timestamp, eg. 4:35:21
    regex_time = re.compile(r"(\d?[:]?\d+[:]\d+)")

    video_chapters = {}

    lines = description.split("\n")
    start_list = []
    chapter_name_list = []
    for line in lines:
        # Check if lines contains timestamp
        result = regex_time.search(line)
        # If timestamp found
        if result is not None:
            # Append start time
            start_list.append(result[0])

            for i, char in enumerate(line):
                if char.isalpha():
                    # Append chapter name
                    chapter_name_list.append(line[i:].lower())
                    break

    for i, chapter in enumerate(chapter_name_list):
        try:
            video_chapters[chapter] = (start_list[i], start_list[i+1])
        except IndexError:
            video_chapters[chapter] = start_list[i], video_length

    return video_chapters


def download_media(
        url_list: list,
        pathname: str = "",
        media_type: int = 1,
) -> list:
    """
    Download media from YouTube given media URL list.

    :param url_list: A list of media URLs to download
    :param pathname: Where to save. Default is current working dir.
    :param media_type: 0 for Video, 1 for Audio. Default 1-Audio
    :return: List of downloaded media
    """

    def download_audio(url):
        yt = YouTube(url)
        file = yt.streams.filter(only_audio=True).first().download(pathname)

        new_file = file.split(".mp4")[0] + ".mp3"
        subprocess.run(['mv', f'{file}', f'{new_file}'])

        return file

    def download_video(url):
        yt = YouTube(url)
        file = yt.streams.filter().get_highest_resolution().download(pathname)

        return file

    try:
        os.chdir(pathname)
    except FileNotFoundError:
        os.mkdir(pathname)
        os.chdir(pathname)

    # If video selected
    if media_type == 0:
        with Pool(os.cpu_count()) as pool:
            file_names = pool.map(download_video, url_list)
            media_list = [name for name in file_names]

    # If audio is selected
    else:
        with Pool(os.cpu_count()) as pool:
            file_names = pool.map(download_audio, url_list)
            media_list = [name for name in file_names]

    return media_list


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

    if filename == "":
        name = re.sub(" ", "", channel.channel_name)
        filename = name + "_videos.csv"

    # Main info list
    videos_info = []

    for video in channel.videos:

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


def extract_matching_chapters(
        dataframe: pd.DataFrame,
        keywords: tuple = ("",),
) -> dict:
    """
    Extracts a dict with YouTube video chapters from a Pandas DataFrame object that match any of the keywords.

    :param dataframe: Pandas DataFrame of the 'channel_videos_list' return form
    :param keywords: List of string keywords to check against video chapters
    :returns: Dict of URLs with matching chapters
    """
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

            chapters_to_extract[url] = {
                'video_name': dataframe.at[i, 'Name'],
                'chapters': chapters,
            }

    return chapters_to_extract


def split_media_chapters(
        folder_path: str,
        chapter_dict: dict,
):
    """
    Given folder with media files, cuts out clips from each one based on dict of chapters
    with name, start and end timestamps.

    :param folder_name: Name of folder containing the media files
    :param chapter_dict: Dict of chapters of extract_matching_chapters type
    :return:
    """
    regex = re.compile("[:;,.|()#-+*!@£$%^&/]")

    def split(video, extension):
        video_name = video['video_name']
        video_name = regex.sub("", video_name)

        filename = video_name + '.' + extension
        chapters = video['chapters']

        # Create new folder with video name
        os.mkdir(video_name)

        message = f"{video_name}\n"
        for chapter in chapters.keys():
            start = chapters[chapter][0]
            end = chapters[chapter][1]
            new_file = chapter + "." + extension

            subprocess.run(['ffmpeg', '-i', f'{filename}', '-ss', f'{start}', '-to', f'{end}',
                           '-c:v', 'copy', '-c:a', 'copy', f'{video_name}/{new_file}'])

            message += f"{chapter}, {start}, {end}\n"

        command = f"echo '{message}' > '{video_name}/info.txt'"
        os.system(command)


    # cd into folder
    os.chdir(folder_path)
    cwd = os.getcwd()
    # Get all video file names
    files = [file for file in os.listdir(cwd)
             if os.path.isfile(os.path.join(cwd, file)) and file != '.DS_Store']

    if len(files) == 0:
        print(f"{folder_path} contains no files.")
        return 0

    extensions = {file.split(".")[-1] for file in files}
    ext = list(extensions)[0]
    args = [(video, ext) for video in chapter_dict.values()]

    with Pool(os.cpu_count()) as pool:
        results = pool.starmap(split, args)
