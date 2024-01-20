"""
Конвертация данных в json
"""

from scripts_data import data_blog, data_author, data_author_profile, \
    data_entry, data_tag, data_comment

from json import dump

with open("json_data/blogs.json", "w", encoding="utf-8") as f:
    dump(data_blog, f, ensure_ascii=False, indent=4)
with open("json_data/authors.json", "w", encoding="utf-8") as f:
    dump(data_author, f, ensure_ascii=False, indent=4)
with open("json_data/authors_profile.json", "w", encoding="utf-8") as f:
    dump(data_author_profile, f, ensure_ascii=False, indent=4)
with open("json_data/entrys.json", "w", encoding="utf-8") as f:
    dump(data_entry, f, ensure_ascii=False, indent=4)
with open("json_data/tags.json", "w", encoding="utf-8") as f:
    dump(data_tag, f, ensure_ascii=False, indent=4)
with open("json_data/comments.json", "w", encoding="utf-8") as f:
    dump(data_comment, f, ensure_ascii=False, indent=4)
