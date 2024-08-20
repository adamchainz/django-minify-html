from __future__ import annotations

from functools import wraps
from typing import Any
from typing import Callable
from typing import TypeVar
from typing import cast

from asgiref.sync import iscoroutinefunction
from django.http.response import HttpResponseBase

ViewFunc = TypeVar("ViewFunc", bound=Callable[..., HttpResponseBase])

_C = TypeVar("_C", bound=Callable[..., Any])


def no_html_minification(view_func: _C) -> _C:
    """
    Mark a view function as excluded from minification by MinifyHtmlMiddleware.
    """

    wrapped_view: Callable[..., Any]

    if iscoroutinefunction(view_func):

        async def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            return await view_func(*args, **kwargs)

    else:

        def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            return view_func(*args, **kwargs)

    wrapped_view.should_minify_html = False  # type: ignore[attr-defined]

    return cast(_C, wraps(view_func)(wrapped_view))
