==================
django-minify-html
==================

.. image:: https://img.shields.io/github/actions/workflow/status/adamchainz/django-minify-html/main.yml.svg?branch=main&style=for-the-badge
   :target: https://github.com/adamchainz/django-minify-html/actions?workflow=CI

.. image:: https://img.shields.io/badge/Coverage-100%25-success?style=for-the-badge
  :target: https://github.com/adamchainz/django-minify-html/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/django-minify-html.svg?style=for-the-badge
   :target: https://pypi.org/project/django-minify-html/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Use `minify-html <https://github.com/wilsonzlin/minify-html>`__, the extremely fast HTML + JS + CSS minifier, with Django.

----

**Work smarter and faster** with my book `Boost Your Django DX <https://adamchainz.gumroad.com/l/byddx>`__ which covers many ways to improve your development experience.

----

Requirements
------------

Python 3.9 to 3.13 supported.

Django 4.2 to 5.2 supported.

Installation
------------

1. Install with **pip**:

   .. code-block:: sh

       python -m pip install django-minify-html

2. Add django-minify-html to your ``INSTALLED_APPS``:

   .. code-block:: python

       INSTALLED_APPS = [
           ...,
           "django_minify_html",
           ...,
       ]

3. Add the middleware:

   .. code-block:: python

       MIDDLEWARE = [
           ...,
           "django_minify_html.middleware.MinifyHtmlMiddleware",
           ...,
       ]

   The middleware should be *below* any other middleware that may encode your responses, such as Django’s |GZipMiddleware|__.
   It should be *above* any that may modify your HTML, such as those of `django-debug-toolbar <https://django-debug-toolbar.readthedocs.io/>`__ or `django-browser-reload <https://pypi.org/project/django-browser-reload/>`__.

   .. |GZipMiddleware| replace:: ``GZipMiddleware``
   __ https://docs.djangoproject.com/en/stable/ref/middleware/#django.middleware.gzip.GZipMiddleware

Reference
---------

For information about what minify-html does, refer to `its documentation <https://github.com/wilsonzlin/minify-html>`__.

``django_minify_html.middleware.MinifyHtmlMiddleware``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The middleware runs ``minify_html.minify()`` on the content of HTML responses.
This function minifies HTML, and any inline JavaScript and CSS.

The middleware passes keyword arguments to ``minify()`` from its ``minify_args`` attribute, a dictionary of names to values.
These correspond to the values in the Rust library’s `Cfg structure <https://docs.rs/minify-html/latest/minify_html/struct.Cfg.html>`__, which have defaults in the Python library as visible `in the source <https://github.com/wilsonzlin/minify-html/blob/master/python/main/src/lib.rs>`__.
By default the middleware overrides ``minify_css`` and ``minify_js`` to ``True``.
If you need to change an argument, subclass the middleware, replace ``minify_args``, and use your subclass.
For example, to preserve comments after minification:

.. code-block:: python

    from django_minify_html.middleware import MinifyHtmlMiddleware


    class ProjectMinifyHtmlMiddleware(MinifyHtmlMiddleware):
        minify_args = MinifyHtmlMiddleware.minify_args | {
            "keep_comments": True,
        }

(This example uses Python 3.9’s `dictionary merge operator <https://docs.python.org/3.9/whatsnew/3.9.html#dictionary-merge-update-operators>`__.)

The middleware applies to all non-streaming, non-encoded HTML responses.
You can skip it on individual views with the ``@no_html_minification`` decorator, documented below.

To restrict it more broadly, you can use a subclass with an overriden ``should_minify()`` method.
This method accepts the ``request`` and ``response``, and returns a ``bool``.
For example, to avoid minification of URL’s with the URL prefix ``/admin/``:

.. code-block:: python

    from django.http import HttpRequest, HttpResponse

    from django_minify_html.middleware import MinifyHtmlMiddleware


    class ProjectMinifyHtmlMiddleware(MinifyHtmlMiddleware):
        def should_minify(self, request: HttpRequest, response: HttpResponse) -> bool:
            return super().should_minify(request, response) and not request.path.startswith(
                "/admin/"
            )

Note that responses are minified even when ``DEBUG`` is ``True``.
This is recommended because HTML minification can reveal bugs in your templates, so it’s best to always work with your HTML as it will appear in production.
Minified HTML is hard to read with “View Source” - it’s best to rely on the inspector in your browser’s developer tools.

``django_minify_html.decorators.no_html_minification``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Apply this decorator to views for which you want to skip HTML minification.

.. code-block:: python

    from django.shortcuts import render

    from django_minify_html.decorators import no_html_minification


    @no_html_minification
    def example_view(request):
        return render(request, "problematic-template.html")

Motivation
----------

HTML minification is an underappreciated techinque for web optimization.
It can yield significant savings, even on top of other tools like compression with Brotli or Gzip.

There is an existing package for HTML minification in Django, `django-htmlmin <https://pypi.org/project/django-htmlmin/>`__.
But it is much slower, since it does the minification in Python.
At time of writing, it is also unmaintained, with no release since March 2019.

There are other minifiers out there, but in benchmarks `minify-html <https://github.com/wilsonzlin/minify-html>`__ surpasses them all.
It’s a really well optimized and tested Rust library, and seems to be the best available HTML minifier.

Historically, Cloudflare provided automatic minification (`removed August 2024 <https://community.cloudflare.com/t/deprecating-auto-minify/655677>`__).
This was convenient at the CDN layer, since it requires no application changes.
But it adds some overhead: non-minified HTML has to first be transferred to the CDN, and the CDN has to parse the response, and recombine it.
It also means that you don’t get to see the potential side effects of minification until your code is live.
Overall it should be faster and more predictable to minify within Django, at the point of HTML generation.
