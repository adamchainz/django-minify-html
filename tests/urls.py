from __future__ import annotations

from django.urls import path

from tests import views

urlpatterns = [
    path("streaming/", views.streaming),
    path("encoded/", views.encoded),
    path("text/", views.text),
    path("html/", views.html),
    path("async/", views.async_),
    path("html-multipart-content-type/", views.html_multipart_content_type),
    path("html-no-content-length/", views.html_no_content_length),
    path("inline-style/", views.inline_style),
    path("admin/about/", views.admin_about),
    path("skip-minification/", views.skip_minification),
]
