from __future__ import annotations

from functools import wraps
from typing import Any
from typing import Callable
from typing import cast
from typing import TypeVar

from django.http.response import HttpResponseBase

ViewFunc = TypeVar("ViewFunc", bound=Callable[..., HttpResponseBase])


def no_html_minification(view_func: ViewFunc) -> ViewFunc:
    """
    Mark a view function as excluded from minification by MinifyHtmlMiddleware.
    """

    def wrapped_view(*args: Any, **kwargs: Any) -> HttpResponseBase:
        return view_func(*args, **kwargs)

    wrapped_view.should_minify_html = False  # type: ignore[attr-defined]
    return cast(
        ViewFunc,
        wraps(view_func)(wrapped_view),
    )
