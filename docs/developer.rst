===========================
Contributing and developing
===========================

.. _Cabby project page: https://github.com/Intelworks/Cabby


Reporting issues
================

_Cabby uses Github's issue tracker. See the `Cabby project page`_ on Github.


Obtaining the source code
=========================

The Cabby source code can be found on Github. See the `Cabby project page`_ on
Github.

Layout
======

The opentaxii repository has the following layout:

* ``docs/`` - Used to build the `documentation
  <http://cabby.readthedocs.org>`_.
* ``cabby/`` - The main Cabby source.
* ``tests/`` - opentaxii tests.


Compiling from source
=====================

After cloning the Github repo, just run this::

   (envname) $ python setup.py install


Running the tests
=================

Almost all Cabby code is covered by the unit tests. Cabby uses *pytest* and
*tox* for running those tests. Type ``make test`` to run the unit tests, or run
``tox`` to run the tests against multiple Python versions.


Generating the documentation
============================

The documentation is written in ReStructuredText (reST) format and processed
using *Sphinx*. Type ``make html`` to build the HTML documentation.
