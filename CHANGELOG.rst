=========
Changelog
=========

1.12.0 (2025-02-06)
-------------------

* Support Django 5.2.

1.11.0 (2024-10-29)
-------------------

* Drop Django 3.2 to 4.1 support.

1.10.0 (2024-10-20)
-------------------

* Drop Python 3.8 support.

* Support Python 3.13.

1.9.0 (2024-08-20)
------------------

* Support Django 5.1.

* Extend the ``@no_html_minification`` decorator to support asynchronous views.

1.8.0 (2024-06-19)
------------------

Accidental, empty release.

1.7.1 (2023-11-16)
------------------

* Fix ASGI compatibility on Python 3.12.

1.7.0 (2023-10-11)
------------------

* Support Django 5.0.

1.6.1 (2023-09-04)
------------------

* Fix the value in the ``Content-Length`` header to correctly count bytes, rather than unicode characters.

  Thanks to Haydn Greatnews in `PR #143 <https://github.com/adamchainz/django-minify-html/pull/143>`__.

1.6.0 (2023-06-14)
------------------

* Support Python 3.12.

1.5.0 (2023-02-25)
------------------

* Support Django 4.2.

1.4.0 (2022-10-31)
------------------

* Support Python 3.11.

* Support Django 4.1.

1.3.0 (2022-05-10)
------------------

* Drop support for Django 2.2, 3.0, and 3.1.

1.2.0 (2022-05-07)
------------------

* Add async support to the middleware, to reduce overhead on async views.

1.1.0 (2022-04-27)
------------------

* Added the ``@no_html_minification`` view decorator.

1.0.0 (2021-12-28)
------------------

* Initial release.
