import os
import re
import subprocess

from tqdm import tqdm
from datetime import datetime
from multiprocessing.dummy import Pool
from subprocess import check_output

from common.image import text_image

from common.resources import (
    list_files,
    list_dirs,
    most_common,
    reduce_text_len,
)
from common.variables import (
    regex_time,
    regex_non_word,
)


def get_chapters(
        description: str,
        media_length: str,
) -> dict:
    """
    Try to extract YouTube media chapters from its description.

    :param description: String to iterate through and look for chapters
    :param media_length: Media length in the %H:%M:%S format as last timestamp
    :returns: Dict with chapters containing name, start time & end time
    """

    media_chapters = {}

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
            media_chapters[chapter] = (start_list[i], start_list[i+1])
        except IndexError:
            media_chapters[chapter] = start_list[i], media_length

    return media_chapters


def split_media_chapters(
        folder_path: str,
        chapters_dict: dict,
) -> list:
    """
    Given folder with media files, cuts out clips from each one based on dict of chapters
    with name, start & end timestamps.

    :param folder_path: Name of folder containing the media files
    :param chapters_dict: Dict of chapters of the 'extract_matching_chapters' type
    :return: List of messages
    """

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
            new_file = regex_non_word.sub("_", chapter) + "." + extension

            subprocess.run(['ffmpeg', '-i', f'{filename}', '-ss', f'{start}', '-to', f'{end}',
                           '-c:v', 'copy', '-c:a', 'copy', f'{media_name}/{new_file}'])

            message += f"{chapter}, {start}, {end}\n"

        os.system(f"""echo "{message}" > "{media_name}"/info.txt""")
        os.system(f"""echo "{media['guest']}" > "{media_name}"/guest.txt""")

        return message

    # cd into folder
    os.chdir(folder_path)

    # Get all video file names
    files = list_files(folder_path)

    assert len(files) > 0, f"{folder_path} contains no files."

    # Get most common file extension and use it as a base
    extensions = [file.split(".")[-1] for file in files]
    ext = most_common(extensions)

    arguments = [(media, ext) for media in chapters_dict.values()]

    with Pool(os.cpu_count()) as pool:
        results = pool.starmap(split_media, arguments)

        messages = [res for res in results]

    # cd back into main directory
    os.chdir("..")

    return messages


def list_image_info(
        folder_path: str,
        out_filename: str = "media.txt",
) -> list:
    """
    For each episode's chapter exports an image with description and whole text file containing
    media to be concatenated.

    :param folder_path: Name of folder containing the media files
    :param out_filename: Name of file to save results to
    :return: List of image file names
    """

    os.chdir(folder_path)

    # List of directories inside current dir
    dirs = list_dirs(folder_path)

    assert len(dirs) > 0, f"{folder_path} contains no directories."

    os.mkdir("images")

    files_list = []
    for directory in tqdm(dirs):

        guest = check_output(['cat', f"{directory}/guest.txt"]).decode('utf-8')
        guest = reduce_text_len(guest, 50)
        with open(f"{directory}/info.txt", 'r') as file:
            text = file.read()
            lines = text.split("\n")

            for chapter in lines[1:]:
                if chapter != "":
                    start, end = regex_time.findall(chapter)
                    chapter_name = regex_time.split(chapter)[0][:-2]
                    chapter_name = reduce_text_len(chapter_name, 50)

                    message = f"Guest:\n\n{guest}\n\n\nChapter:\n\n{chapter_name}"
                    title = regex_non_word.sub("_", chapter_name)
                    image_name = f"{directory}/{title}.png"
                    # Create image for the chapter
                    text_image(message, image_name, text_size=35)

                    try:
                        start = datetime.strptime(start, "%H:%M:%S")
                    except ValueError:
                        start = datetime.strptime(start, "%M:%S")
                    try:
                        end = datetime.strptime(end, "%H:%M:%S")
                    except ValueError:
                        end = datetime.strptime(end, "%M:%S")

                    duration = end - start

                    # Write filename of image and duration to list
                    os.system(f"""echo "file '{folder_path}/{image_name}'" >> images/{out_filename}""")
                    os.system(f"echo duration {duration} >> images/{out_filename}")

                    files_list.append(f"{folder_path}/{image_name}")

    # Add last filename again due to ffmpeg quirk
    os.system(f"""echo "file '{folder_path}/{image_name}'" >> images/{out_filename}""")

    return files_list


def list_chapters_and_info(
        folder_path: str,
        file_extension: str = "",
        out_filename: str = "media.txt",
) -> list:
    """
    Given a directory containing directories with chapters, outputs a file listing them.

    :param folder_path: Name of folder containing the media files
    :param file_extension: Name of file extension
    :param out_filename: Name of file to save results to
    :return: List of relative file locations of media to be concatenated
    """
    os.chdir(folder_path)

    # List of directories inside current dir
    dirs = list_dirs(folder_path)

    # List of files inside current dir
    files = list_files(folder_path)

    # Get most common file extension and use it as a base
    if file_extension == "":
        extensions = [file.split(".")[-1] for file in files]
        file_extension = most_common(extensions)

    assert len(dirs) > 0, f"{folder_path} contains no directories."

    files_list = []
    start_time = datetime.strptime("00:00:00", "%H:%M:%S")
    for directory in dirs:

        file_location = f"{folder_path}/{directory}/*.{file_extension}"
        # Write absolute filepath for concatenation
        os.system(f"""for f in {file_location};"""
                  f"""do echo "file '$f'" >> {folder_path}/{out_filename}; done""")
        files_list.append(file_location)

        with open(f"{directory}/info.txt", 'r') as file:
            text = file.read()
            lines = text.split("\n")
            podcast_name = lines[0]

            # Write Episode name for concat video description
            os.system(f"echo '{podcast_name}' >> concat_info.txt")

            for chapter in lines[1:]:
                if chapter != "":
                    start, end = regex_time.findall(chapter)
                    chapter_name = regex_time.split(chapter)[0][:-2]

                    try:
                        start = datetime.strptime(start, "%H:%M:%S")
                    except ValueError:
                        start = datetime.strptime(start, "%M:%S")
                    try:
                        end = datetime.strptime(end, "%H:%M:%S")
                    except ValueError:
                        end = datetime.strptime(end, "%M:%S")

                    duration = end - start

                    # Write timestamp & chapter name of Episode for concat video description
                    os.system(f"echo '{start_time.time()}' - '{chapter_name}' >> concat_info.txt")

                    start_time += duration

    return files_list
