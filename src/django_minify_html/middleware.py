from __future__ import annotations

from collections.abc import Awaitable
from typing import Callable

import minify_html
from asgiref.sync import iscoroutinefunction
from asgiref.sync import markcoroutinefunction
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseBase


class MinifyHtmlMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(
        self,
        get_response: (
            Callable[[HttpRequest], HttpResponseBase]
            | Callable[[HttpRequest], Awaitable[HttpResponseBase]]
        ),
    ) -> None:
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(self.get_response)

        if self.async_mode:
            # Mark the class as async-capable, but do the actual switch
            # inside __call__ to avoid swapping out dunder methods
            markcoroutinefunction(self)

    def __call__(
        self, request: HttpRequest
    ) -> HttpResponseBase | Awaitable[HttpResponseBase]:
        if self.async_mode:
            return self.__acall__(request)
        response = self.get_response(request)
        assert isinstance(response, HttpResponseBase)
        self.maybe_minify(request, response)
        return response

    async def __acall__(self, request: HttpRequest) -> HttpResponseBase:
        result = self.get_response(request)
        assert not isinstance(result, HttpResponseBase)  # type narrow
        response = await result
        self.maybe_minify(request, response)
        return response

    def maybe_minify(self, request: HttpRequest, response: HttpResponseBase) -> None:
        if self.should_minify(request, response):
            assert isinstance(response, HttpResponse)
            content = response.content.decode(response.charset)
            minified_content = minify_html.minify(content, **self.minify_args)
            response.content = minified_content
            if "Content-Length" in response:
                response["Content-Length"] = len(response.content)

    minify_args = {
        "minify_css": True,
        "minify_js": True,
    }

    def should_minify(self, request: HttpRequest, response: HttpResponseBase) -> bool:
        return (
            not getattr(response, "streaming", False)
            and (
                request.resolver_match is None
                or getattr(request.resolver_match.func, "should_minify_html", True)
            )
            and response.get("Content-Encoding", "") == ""
            and response.get("Content-Type", "").split(";", 1)[0] == "text/html"
        )
