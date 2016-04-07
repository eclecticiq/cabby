===========================
Contributing and developing
===========================

.. _cabby project page: https://github.com/EclecticIQ/cabby


Reporting issues
================

Cabby uses Github's issue tracker. See the `Cabby project page`_ on Github.


Obtaining the source code
=========================

The Cabby source code can be found on Github. See the `Cabby project page`_ on
Github.

Layout
======

The Cabby repository has the following layout:

* ``docs/`` - used to build the `documentation <http://cabby.readthedocs.org>`_;
* ``cabby/`` - source code;
* ``tests/`` - tests.


Compiling from source
=====================

After cloning the Github repo, just run::

   $ python setup.py install


Running the tests
=================

Almost all Cabby code is covered by the unit tests. Cabby uses `py.test <http://pytest.org/latest/>`_ and
`tox <http://tox.readthedocs.org/en/latest/>`_ for running tests. Type ``tox -r`` or ``py.test`` to run the unit tests.


Generating the documentation
============================

The documentation is written in `ReStructuredText <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_ (reST) format and processed
using `Sphinx <http://sphinx-doc.org/>`_. To build HTML documentation, go to ``docs`` and type ``make html``.

.. rubric:: Next steps

Continue to :doc:`License <license>`.

.. vim: set spell spelllang=en:
