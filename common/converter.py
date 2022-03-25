import os
import re

from subprocess import check_output
from datetime import datetime
from common.variables import regex_time
from common.image import text_image
from tqdm import tqdm

from common.resources import (
    list_files,
    list_files_paths,
    list_dirs,
    most_common,
    reduce_text_len,
)


def list_image_info(
        folder_path: str,
        out_filename: str = "media.txt",
) -> list:
    """
    For each episode chapter exports an image with description and whole text file containing
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
            podcast_name = lines[0]

            for chapter in lines[1:]:
                if chapter != "":
                    start, end = regex_time.findall(chapter)
                    chapter_name = regex_time.split(chapter)[0][:-2]
                    chapter_name = reduce_text_len(chapter_name, 50)

                    message = f"Guest:\n\n{guest}\n\n\nChapter:\n\n{chapter_name}"
                    title = re.sub(" ", "_", chapter_name)
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


def concat_images_list(
        folder_path: str,
        media_list: str = "media.txt",
        out_filename: str = "concat_images.mp4",
) -> None:
    """
    Concatenates images into a video file.

    :param folder_path: Name of dir containing images folder
    :param media_list: Text file with image names and durations
    :param out_filename: Name of output file
    :return:
    """

    os.chdir(folder_path + "/images")

    os.system(f"ffmpeg -f concat -safe 0 -i {media_list} -vsync vfr -pix_fmt yuv420p {out_filename}")


def add_audio_to_video(
        folder_path: str,
        video_file: str,
        audio_file: str,
        out_filename: str = "final_video.mp4",
) -> None:
    """
    Adds audio stream to video stream. If existing video has audio, it will be replaced.

    :param folder_path: Name of folder containing files.
    :param video_file: Name of video file
    :param audio_file: Name of audio file
    :param out_filename: Name of output file
    :return: None
    """
    os.chdir(folder_path)

    os.system(f"ffmpeg -i images/{video_file} -i {audio_file} -c:v copy -c:a aac {out_filename}")


def concat_media_demuxer(
        folder_path: str,
        media_list: str = "media.txt",
        out_filename: str = "concat_media.mp4",
) -> str:
    """
    ffmpeg Concat Demuxer a series of media files of the same type in a single one.

    :param folder_path: Name of folder containing media_list
    :param media_list: Name of Text file containing media to be concatenated
    :param out_filename: Name of output file including extension, eg. 'media.mp4'
    :return: Relative filepath of output file
    """
    os.chdir(folder_path)
    command = f"ffmpeg -f concat -safe 0 -i '{media_list}' -c copy '{out_filename}'"

    os.system(command)

    return f"{folder_path}/{out_filename}"


def concat_media_demuxer_filter(
        folder_path: str,
        media_list: str = "media.txt",
        out_filename: str = "concat_media.mp4",
        video_codec: str = 'h264',
) -> str:
    """¨
    ffmpeg concat demuxer with filter a series of media files in a single one.

    :param folder_path: Name of folder containing media_list
    :param media_list: Name of Text file containing media to be concatenated
    :param out_filename: Name of output file including extension, eg. 'media.mp4'
    :param video_codec: ffmpeg filter type
    :return: Relative filepath of output file
    """
    os.chdir(folder_path)
    command = f"ffmpeg -f concat -safe 0 -i '{media_list}' -c:v {video_codec} -c:a copy '{out_filename}'"

    os.system(command)

    return f"{folder_path}/{out_filename}"


def concat_media_chapters(
        folder_path: str,
        out_filename: str = "concat_media.mp4",
        media_list: str = "media.txt",
) -> None:
    """
    Searches all directories in provided dir and concatenates their clips into a single file.

    :param folder_path: Name of folder containing the media files
    :param out_filename: :param filename: Name of output file including extension
    :param media_list: Name of input file to read
    :return: Concatenated video of clips in each folder in directory
    """

    os.chdir(folder_path)
    cwd = os.getcwd()
    # List of directories inside current dir
    dirs = list_dirs(folder_path)

    assert len(dirs) > 0, f"{folder_path} contains no directories."

    # List of files inside current dir
    files = list_files(folder_path)

    # Get most common file extension and use it as a base
    extensions = [file.split(".")[-1] for file in files]
    file_extension = most_common(extensions)

    for directory in dirs:
        os.chdir(cwd + "/" + f"{directory}")
        folder_dir = os.getcwd()

        # write path locations of chapters to .txt file
        os.system(f"""for f in *.{file_extension};"""
                  f"""do echo "file '$f'" >> {folder_dir}/{media_list}; done""")

        concat_media_demuxer(folder_dir, media_list, out_filename)


def concat_media_chapters_and_images(
        folder_path: str,
        out_filename: str = "concat_media.mp4",
        file_extension: str = "mp4",
) -> None:

    os.chdir(folder_path)

    # List of directories inside current dir
    dirs = list_dirs(folder_path)

    assert len(dirs) > 0, f"{folder_path} contains no directories."

    for directory in dirs:
        os.chdir(folder_path + "/" + directory)
        cwd = os.getcwd()

        # List all media files
        files = [file for file in list_files(cwd)
                 if file.endswith(f".{file_extension}") is True]

        for file in files:
            file_name = re.split(f".{file_extension}", file)[0]

            # Combine chapter audio and image into a video
            os.system(f"ffmpeg -i {file_name}.png -i {file_name}.{file_extension} -c:v libx264 "
                      f"-tune stillimage -c:a copy chapter_{file_name}.{file_extension}")

            # Append chapter file name for later concat
            os.system(f"""echo "file 'chapter_{file_name}.{file_extension}'" >> media.txt""")
        # Concat all chapter videos into one
        concat_media_demuxer(cwd, "media.txt", out_filename)

        os.system(f"""echo "file '{directory}/{out_filename}'" >> {folder_path}/media.txt""")


def concat_video_files_filter(
        folder_path: str,
        out_filename: str = "concat_media.mp4",
) -> None:
    """
    Given a directory it searches for the same filename in each of them and concatenates all.

    :param folder_path:  Name of folder containing the media files
    :param out_filename: Name of file to concatenate
    :return:
    """

    os.chdir(folder_path)
    files = []
    dirs = list_dirs(folder_path)
    for directory in dirs:
        files.append(f"{directory}/{out_filename}")

    base_file = files[0]
    count = 2
    out_files = []
    for file in files[1:]:
        extension = '.mp4'
        out_file = 'Whole_file' + str(count)
        command = f"""
        ffmpeg -i '{base_file}' -i '{file}' \
        -filter_complex "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]" \
        -map "[outv]" -map "[outa]" '{out_file}{extension}'
        """
        base_file = out_file + extension
        out_files.append(out_file + extension)
        count += 1
        os.system(command)

        if len(out_files) > 1:
            os.system(f"rm '{out_files[0]}'")
            out_files.pop(0)


def convert_media(
        folder_path: str,
        video_codec: str = 'copy',
        audio_codec: str = 'copy',
        file_extension: str = 'mkv'
) -> list:
    """
    Converts all videos from file into new ones with different codecs.

    :param folder_path:   Name of folder containing the media files
    :param video_codec: Name of video codec to apply
    :param audio_codec: Name of audio codec to apply
    :param file_extension: Name of new output file extension
    :return: List of new filenames
    """
    os.chdir(folder_path)
    files = list_files_paths(folder_path)

    out_files = []
    for file in files:
        out_file = file.split(".")[0]
        out_file += "." + file_extension

        command = f"ffmpeg -i {file} -c:v {video_codec} -c:a {audio_codec} {out_file}"
        p = os.popen(command, 'w')
        p.write("y\n")

        out_files.append(out_file)

    return out_files
