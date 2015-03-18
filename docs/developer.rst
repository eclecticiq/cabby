===========================
Contributing and developing
===========================

.. _cabby project page: https://github.com/Intelworks/cabby


Reporting issues
================

cabby uses Github's issue tracker. See the `cabby project page`_ on Github.


Obtaining the source code
=========================

The cabby source code can be found on Github. See the `cabby project page`_ on
Github.

Layout
======

The opentaxii repository has the following layout:

* ``docs/`` - Used to build the `documentation
  <http://cabby.readthedocs.org>`_.
* ``cabby/`` - The main cabby source.
* ``tests/`` - opentaxii tests.


Compiling from source
=====================

After cloning the Github repo, just run this::

   $ python setup.py install


Running the tests
=================

Almost all cabby code is covered by the unit tests. cabby uses *pytest* and
*tox* for running those tests. Type ``make test`` to run the unit tests, or run
``tox`` to run the tests against multiple Python versions.


Generating the documentation
============================

The documentation is written in ReStructuredText (reST) format and processed
using *Sphinx*. Type ``make html`` to build the HTML documentation.
