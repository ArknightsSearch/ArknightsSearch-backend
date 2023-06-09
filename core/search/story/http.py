import re

from pydantic import BaseModel

from fastapi import Query

from core.server import app
from core.constant import support_language
from .search import search, StorySearchParamGroup
from .data import *
from .extra import *


class Result(BaseModel):
    name: str
    zone: str
    type: str
    data: list[ExtraData]


class Response(BaseModel):
    total: int
    has_more: bool
    data: list[Result]


class Request(BaseModel):
    params: StorySearchParamGroup
    lang: support_language = 'zh_CN'
    limit: int = Query(ge=1, le=100, default=20)
    offset: int = Query(ge=0, default=0)


def format_result(result: list[str], lang: support_language, extra: Extra):
    return [{
        'name': story_data[i]['name'][lang],
        'zone': zone_name[story_data[i]['zone']][lang],
        'type': story_data[i]['type'],
        'data': extra.get(i)
    } for i in result]


@app.post('/story')
def search_story(req: Request) -> Response:
    # TODO 适配结果
    result = list(sorted(search(req.params)))
    total = len(result)
    has_more = False

    if req.offset > len(result):
        result = []
    else:
        result = result[req.offset:]
        if len(result) > req.limit:
            result = result[:req.limit]
            has_more = True

    return Response(
        total=total,
        has_more=has_more,
        data=format_result(result, req.lang, Extra(req.params))
    )
