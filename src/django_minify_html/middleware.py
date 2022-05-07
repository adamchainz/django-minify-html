from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine

import minify_html
from django.http import HttpRequest
from django.http.response import HttpResponseBase


class MinifyHtmlMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response
        if asyncio.iscoroutinefunction(self.get_response):
            # Mark the class as async-capable, but do the actual switch
            # inside __call__ to avoid swapping out dunder methods
            self._is_coroutine = (
                asyncio.coroutines._is_coroutine  # type: ignore [attr-defined]
            )
        else:
            self._is_coroutine = None

    def __call__(
        self, request: HttpRequest
    ) -> HttpResponseBase | Coroutine[Any, Any, Any]:
        if self._is_coroutine:
            return self.__acall__(request)
        response = self.get_response(request)
        self.maybe_minify(request, response)
        return response

    async def __acall__(
        self, request: HttpRequest
    ) -> Coroutine[Any, Any, HttpResponseBase]:
        response = await self.get_response(request)
        self.maybe_minify(request, response)
        return response

    def maybe_minify(self, request: HttpRequest, response: HttpResponseBase) -> None:
        if self.should_minify(request, response):
            content = response.content.decode(response.charset)
            minified_content = minify_html.minify(content, **self.minify_args)
            response.content = minified_content
            if "Content-Length" in response:
                response["Content-Length"] = len(minified_content)

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
