from typing import Callable

import minify_html
from django.http import HttpRequest, HttpResponse


class MinifyHtmlMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if self.should_minify(request, response):
            content = response.content.decode(response.charset)
            minified_content = minify_html.minify(content, **self.minify_args)
            response.content = minified_content
            if "Content-Length" in response:
                response["Content-Length"] = len(minified_content)
        return response

    minify_args = {
        "minify_css": True,
        "minify_js": True,
    }

    def should_minify(self, request: HttpRequest, response: HttpResponse) -> bool:
        return (
            not getattr(response, "streaming", False)
            and response.get("Content-Encoding", "") == ""
            and response.get("Content-Type", "").split(";", 1)[0] == "text/html"
        )
