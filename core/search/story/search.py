import re
from typing import Literal
from pydantic import BaseModel

from .data import *

c1 = re.compile(r'\s')


def search_text(*text: str) -> list[set[str]]:
    return [text_index.get(i, set()) for i in set(c1.sub('', ' '.join(text)))]


def search_char(char: str) -> set[str]:
    result = [char_index.get(i, set()) for i in char_name2id[char]]
    if len(result) > 1:
        result = result[0].union(*result[1:])
    elif result:
        result = result[0]
    else:
        result = set()

    return result


def search_zone(zone: str) -> list[set[str]]:
    return zone_index.get(zone, set())


SearchMethod = {
    'char': search_char,
    'zone': search_zone
}


class StorySearchParam(BaseModel):
    type: Literal['text', 'zone', 'char']
    param: str
    raw: str = None


StorySearchParamGroup = list[StorySearchParam]


def search(params: StorySearchParamGroup) -> set[str]:
    text_group = [p.param for p in params if p.type == 'text']
    result = search_text(*text_group) + [SearchMethod[p.type](p.param) for p in params if p.type != 'text']

    if len(result) > 1:
        result = result[0].intersection(*result[1:])
    elif result:
        result = result[0]
    else:
        result = set()

    if text_group:
        for story in result.copy():
            text = text_data['zh_CN'][story]
            for t in text_group:
                if t not in text:
                    result.remove(story)
                    break

    return result
