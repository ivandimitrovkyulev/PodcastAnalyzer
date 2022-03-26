import re


# Compiled regex matching media timestamp, eg. '01:54:35' (%H:%M:%S)
regex_time = re.compile(r"(\d?[:]?\d+[:]\d+)")

# Compiled regex matching any non-word characters
regex_non_word = re.compile(r"[^\w]+|[_]+")

column_names = (
    'Name',
    'URL_Link',
    'Length',
    'Views',
    "Publish_date",
    'Description',
    'Keywords',
    'Author',
    'ID'
)
