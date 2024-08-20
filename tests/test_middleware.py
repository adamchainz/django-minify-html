from __future__ import annotations

from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.test import SimpleTestCase
from django.test import override_settings

from django_minify_html.middleware import MinifyHtmlMiddleware
from tests.views import basic_html
from tests.views import basic_html_minified


class NoCssMiddleware(MinifyHtmlMiddleware):
    minify_args: dict[str, bool] = {}


class NoAdminMiddleware(MinifyHtmlMiddleware):
    def should_minify(self, request: HttpRequest, response: HttpResponseBase) -> bool:
        return super().should_minify(request, response) and not request.path.startswith(
            "/admin/"
        )


class MinifyHtmlMiddlewareTests(SimpleTestCase):
    def test_streaming_response(self):
        response = self.client.get("/streaming/")

        assert response.getvalue() == basic_html

    def test_encoded_response(self):
        response = self.client.get("/encoded/")

        assert response.content == basic_html

    def test_text_response(self):
        response = self.client.get("/text/")

        assert response.content == basic_html

    def test_success(self):
        response = self.client.get("/html/")

        assert response.content == basic_html_minified
        assert response["Content-Length"] == str(len(basic_html_minified))

    async def test_async(self):
        response = await self.async_client.get("/async/")

        assert response.content == basic_html_minified
        assert response["Content-Length"] == str(len(basic_html_minified))

    def test_multipart_content_type(self):
        response = self.client.get("/html-multipart-content-type/")

        assert response.content == basic_html_minified

    def test_no_content_length(self):
        response = self.client.get("/html-no-content-length/")

        assert response.content == basic_html_minified
        assert "Content-Length" not in response

    def test_subclass_different_args(self):
        with override_settings(MIDDLEWARE=[f"{__name__}.NoCssMiddleware"]):
            response = self.client.get("/inline-style/")

        # CSS minfication would collapse spaces
        assert response.content == b"<style>body { background: salmon; }</style>"

    def test_subclass_ignore_path(self):
        with override_settings(MIDDLEWARE=[f"{__name__}.NoAdminMiddleware"]):
            response = self.client.get("/admin/about/")

        assert response.content == basic_html

    def test_decorator(self):
        response = self.client.get("/skip-minification/")

        assert response.content == basic_html

    async def test_decorator_async(self):
        response = await self.async_client.get("/skip-minification-async/")

        assert response.content == basic_html
