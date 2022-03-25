import os
from common.variables import regex_time


def get_chapters(
        description: str,
        media_length: str,
) -> dict:
    """
    Attempt to extract YouTube media chapters from its description.

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


def delete_redundant_dirs(path: str) -> None:
    os.chdir(path)

    files = set([file.split(".")[0] for file in list_files(path)])
    dirs = set(list_dirs(path))

    diff = dirs.difference(files)
    for dif in diff:
        os.system(f"rm -r {dif}")


def most_common(list_):
    return max(set(list_), key=list_.count)


def list_dirs(folder_path: str,) -> list:
    """
    Returns a list of all directories in a specified directory.

    :param folder_path: Path to directory to inspect
    :return: List of paths of all directories
    """

    dirs = [directory for directory in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, directory)) and directory[0] != '.']

    return dirs


def list_files(folder_path: str,) -> list:
    """
    Returns a list of all files in a specified directory.

    :param folder_path: Path to directory to inspect
    :return: List of paths of all files
    """

    files = [file for file in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, file)) and file[0] != '.']

    return files


def list_dirs_paths(folder_path: str,) -> list:
    """
    Returns a list of all directory paths in a specified directory.

    :param folder_path: Path to directory to inspect
    :return: List of paths of all directories
    """

    dirs = [f"{folder_path}/{directory}" for directory in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, directory)) and directory[0] != '.']

    return dirs


def list_files_paths(folder_path: str,) -> list:
    """
    Returns a list of all file paths in a specified directory.

    :param folder_path: Path to directory to inspect
    :return: List of paths of all files
    """

    files = [f"{folder_path}/{file}" for file in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, file)) and file[0] != '.']

    return files


def rename_file_extension(
        folder_path: str,
        new_extension: str,
) -> list:
    """
    Iterates through all files in given dir and those that match extension get renamed.

    :param folder_path: Name of folder containing the files
    :param new_extension: Name of file extension to be given with dot, eg. '.wav'
    :return: List of renamed files
    """
    os.chdir(folder_path)

    # Get all files in directory
    files = list_files(folder_path)

    renamed_files = []
    for file in files:
        name = file.split(".")[0]
        name += new_extension
        command = f"""mv {file} {name}"""
        os.system(command)

        renamed_files.append(name)

    return renamed_files


def reduce_text_len(
        text: str,
        max_len: int,
) -> str:
    """Takes a string as input and returns a reduced line length string, where
    each line has a maximum specified character length. Achieved by inserting \n

    :param text: String to be transformed
    :param max_len: Maximum number of characters per line returned
    """

    if type(text) != str:
        raise Exception("Parameters text & max_len must be str & int respectively.")

    reduced_text = ""
    text_len = len(text)
    if text_len <= max_len:
        return text
    else:
        count = 1
        current_word = ""
        for char in text:

            if char.isspace():
                reduced_text += current_word
                current_word = ""

                if count >= max_len:
                    reduced_text += "\n"
                    count = 0  # Reset counter
                else:
                    reduced_text += char
                    count += 1  # Increment

            else:
                current_word += char
                count += 1  # Increment

        reduced_text += current_word

        return reduced_text
