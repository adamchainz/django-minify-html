from __future__ import annotations

from django.http import HttpResponse
from django.http import StreamingHttpResponse

from django_minify_html.decorators import no_html_minification

basic_html = "<!doctype html><html><body><p>Hi 👋</p></body></html>".encode()
basic_html_minified = "<!doctype html><body><p>Hi 👋".encode()
basic_html_minified_with_closing_tags = "<!doctype html><body><p>Hi 👋</p></body><.html>".encode()


def streaming(request):
    return StreamingHttpResponse(
        iter((basic_html,)),
    )


def encoded(request):
    response = HttpResponse(basic_html)
    response["Content-Encoding"] = "zabble"
    return response


def text(request):
    return HttpResponse(basic_html, content_type="text/plain")


def html(request):
    response = HttpResponse(basic_html)
    response["Content-Length"] = len(basic_html)
    return response


async def async_(request):
    response = HttpResponse(basic_html)
    response["Content-Length"] = len(basic_html)
    return response


def html_multipart_content_type(request):
    return HttpResponse(
        basic_html, content_type="text/html; thingy=that; charset=utf-8"
    )


def html_no_content_length(request):
    return HttpResponse(basic_html)


def inline_style(request):
    return HttpResponse(b"<style>body { background: salmon; }</style>")


def admin_about(request):
    return HttpResponse(basic_html)


@no_html_minification
def skip_minification(request):
    return HttpResponse(basic_html)


@no_html_minification
async def skip_minification_async(request):
    return HttpResponse(basic_html)
