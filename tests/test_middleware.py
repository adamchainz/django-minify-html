from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.test import RequestFactory, SimpleTestCase

from django_minify_html.middleware import MinifyHtmlMiddleware


class HtmxMiddlewareTests(SimpleTestCase):
    basic_html = b"<!doctype html><html><body><p>Hi</p></body></html>"
    basic_html_minified = b"<!doctypehtml><body><p>Hi"

    request_factory = RequestFactory()

    def setUp(self):
        self.request = self.request_factory.get("/")
        self.response = HttpResponse(self.basic_html)

        def get_response(request: HttpRequest) -> HttpResponse:
            response = self.response
            if not getattr(response, "streaming", False):
                response["Content-Length"] = len(response.content)
            return response

        self.middleware = MinifyHtmlMiddleware(get_response)

    def test_streaming_response(self):
        self.response = StreamingHttpResponse(iter([self.basic_html]))

        response = self.middleware(self.request)

        content = b"".join(response.streaming_content)
        assert content == self.basic_html

    def test_encoded_response(self):
        self.response["Content-Encoding"] = "zabble"

        response = self.middleware(self.request)

        assert response.content == self.basic_html

    def test_text_response(self):
        self.response["Content-Type"] = "text/plain"

        response = self.middleware(self.request)

        assert response.content == self.basic_html

    def test_success(self):
        response = self.middleware(self.request)

        assert response.content == self.basic_html_minified
        assert response["Content-Length"] == str(len(self.basic_html_minified))

    def test_multipart_content_type(self):
        self.response["Content-Type"] = "text/html; thingy=that; charset=utf-8"

        response = self.middleware(self.request)

        assert response.content == self.basic_html_minified

    def test_no_content_length(self):
        def get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse(self.basic_html)

        middleware = MinifyHtmlMiddleware(get_response)

        response = middleware(self.request)

        assert response.content == self.basic_html_minified
        assert "Content-Length" not in response

    def test_subclass_different_args(self):
        class NoCss(MinifyHtmlMiddleware):
            minify_args = {}

        orig_content = b"<style>body { background: salmon; }</style>"
        response = HttpResponse(orig_content)

        def get_response(request: HttpRequest) -> HttpResponse:
            return response

        middleware = NoCss(get_response)

        response = middleware(self.request)

        assert response.content == orig_content

    def test_subclass_ignore_path(self):
        class NoAdmin(MinifyHtmlMiddleware):
            def should_minify(
                self, request: HttpRequest, response: HttpResponse
            ) -> bool:
                return super().should_minify(
                    request, response
                ) and not request.path.startswith("/admin/")

        def get_response(request: HttpRequest) -> HttpResponse:
            return self.response

        middleware = NoAdmin(get_response)
        request = self.request_factory.get("/admin/")

        response = middleware(request)

        assert response.content == self.basic_html
