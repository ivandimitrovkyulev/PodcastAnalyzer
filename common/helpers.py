import re
import pandas as pd
from datetime import timedelta
from pytube import Channel, YouTube


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


def download_audio(
        url_dict: dict,
        pathname: str = "",
):

    for url in url_dict.keys():
        yt = YouTube(url)
        yt.streams.filter(only_audio=True).first().download(pathname)


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


def extract_chapters(
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
