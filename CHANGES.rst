Changelog
=========

0.1.18 (2017-06-19)
-------------------
* Dependencies upgraded (`changes <https://github.com/EclecticIQ/cabby/commit/be491ccf457b8b989982a8d49634e905d04bf31b>`_).
* ``timeout`` property that sets HTTP timeout added to the client class and CLI tools (thanks `@joarleymoraes <https://github.com/joarleymoraes>`_).

0.1.17 (2017-04-03)
-------------------
* Support for XML "huge trees" added. It can be disabled with environment variable. See :ref:`configuration_via_env_vars`.

0.1.16 (2016-10-31)
-------------------
* Support for gzipped responses added.

0.1.15 (2016-10-19)
-------------------
* Issue with unrecognized TLS key password is fixed.

0.1.14 (2016-10-19)
-------------------
* Issue when Cabby was assuming port 80 for HTTPS URLs is fixed.

0.1.13 (2016-10-18)
-------------------
* Cabby will always return content block body as bytes.
* JWT token caching added.
* Added support for local TLS CA files.
* ``--port`` option in CLI commands gets a higher priority than port extracted from provided ``--path``.
* Docker file moved to ``alpine`` as a base, shaving off 520MB from the total size of the container.

0.1.12 (2016-06-13)
-------------------
* fix for incorrect connection error handling issue, that was affecting invalid connections with tls and key password.

0.1.11 (2016-04-27)
-------------------
* Documentation fixes.

0.1.10 (2015-12-29)
-------------------
* Removing incorrect assumption that auth details are always present.

0.1.9 (2015-12-04)
------------------
* Own implementation of TAXII transport logic added, using `Requests <http://python-requests.org/>`_ library for most of the requests.
* Added ``taxii-proxy`` CLI command to allow funneling of data from one taxii server to another.
* Various bug fixes.

0.1.7 (2015-09-18)
------------------
* Fix for XML stream parser issue related to a race condition in libxml.

0.1.6 (2015-08-11)
------------------
* Missing dependencies added to setup.py.

0.1.5 (2015-08-10)
------------------
* Added Python 3 compatibility.
* XML stream parsing for Poll Response messages.
* Bugfixes.

0.1.4 (2015-07-24)
------------------
* ``--bindings`` option added for ``taxii-poll`` CLI command.
* Pagination issue, triggered during processing of paged Poll response, was fixed.
* CLI datetime parameters have UTC timezone by default.
* JWT based authentication method added.
* Multiple naming, style and bug fixes.

0.1.3 (2015-04-08)
------------------
* Workaround for libtaxii issue #186 (wrapping incorrect response in Status Message) has been added.
* Tests improved.

0.1.2 (2015-03-31)
------------------
* Issue with proxy arguments being ignored is fixed.
* Issue with poll results print in CLI referencing wrong entity is fixed.
* Wording and style fixes.

0.1.1 (2015-03-26)
------------------
* Tidying up packaging and distribution related configuration.

0.1.0 (2015-03-26)
------------------
* Initial release.
