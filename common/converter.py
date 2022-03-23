import os
from common.resources import (
    list_files,
    list_files_paths,
    list_dirs,
    most_common,
)


def list_chapters(
        folder_path: str,
        file_name: str = "media.txt",
) -> list:
    """
    Given a directory containing directories with chapters, outputs a file listing them.

    :param folder_path: Name of folder containing the media files
    :param file_name: Name of file to save results to
    :return: List of relative file locations of media to be concatenated
    """
    os.chdir(folder_path)

    # List of directories inside current dir
    dirs = list_dirs(folder_path)

    # List of files inside current dir
    files = list_files(folder_path)

    # Get most common file extension and use it as a base
    extensions = [file.split(".")[-1] for file in files]
    file_extension = most_common(extensions)

    assert len(dirs) > 0, f"{folder_path} contains no directories."

    files_list = []
    for directory in dirs:
        file_location = f"'{directory}'/*.{file_extension}"
        os.system(f"""for f in {file_location};"""
                  f"""do echo "file '$f'" >> {folder_path}/{file_name}; done""")

        files_list.append(file_location)

    return files_list


def concat_media_demuxer(
        folder_path: str,
        media_list: str,
        filename: str = "concat_media.mp4",
) -> str:
    """
    ffmpeg concat demuxer a series of media files in a single one.

    :param folder_path: Name of folder containing media_list
    :param media_list: Name of Text file containing media to be concatenated
    :param filename: Name of output file including extension, eg. 'media.mp4'
    :return: Relative filepath of output file
    """
    os.chdir(folder_path)
    command = f"ffmpeg -f concat -safe 0 -i '{media_list}' -c copy '{filename}'"

    os.system(command)

    return f"{folder_path}/{filename}"


def concat_media_demuxer_filter(
        folder_path: str,
        media_list: str,
        filename: str = "concat_media.mp4",
        video_codec: str = 'h264',
) -> str:
    """¨
    ffmpeg concat demuxer with filter a series of media files in a single one.

    :param folder_path: Name of folder containing media_list
    :param media_list: Name of Text file containing media to be concatenated
    :param filename: Name of output file including extension, eg. 'media.mp4'
    :param video_codec: ffmpeg filter type
    :return: Relative filepath of output file
    """
    os.chdir(folder_path)
    command = f"ffmpeg -f concat -safe 0 -i '{media_list}' -c:v {video_codec} -c:a copy '{filename}'"

    os.system(command)

    return f"{folder_path}/{filename}"


def concat_media_chapters(
        folder_path: str,
        filename: str = "concat_media.mp4",
) -> None:
    """
    Searches all directories in provided dir and concatenates their clips into a single file.

    :param folder_path: Name of folder containing the media files
    :param filename: :param filename: Name of output file including extension
    :return: Concatenated video of clips in each folder in directory
    """
    media_list = "media.txt"

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

        concat_media_demuxer(folder_dir, media_list, filename)


def concat_video_files_filter(
        folder_path: str,
        filename: str = "concat_media.mp4",
) -> None:
    """
    Given a directory it searches for the same filename in each of them and concatenates all.

    :param folder_path:  Name of folder containing the media files
    :param filename: Name of file to concatenate
    :return:
    """

    os.chdir(folder_path)
    files = []
    dirs = list_dirs(folder_path)
    for directory in dirs:
        files.append(f"{directory}/{filename}")

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
