Changelog for cabby
===================

0.1.7 (2015-09-16)
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
