==================
Installation guide
==================

.. highlight:: sh

This guide provides installation instructions for cabby.


Build and install cabby
=======================

You can automatically install the latest cabby release from the `Python
Package Index <http://pypi.python.org/>`_ (PyPI) using ``pip``::

   (envname) $ pip install --process-dependency-links cabby

``--process-dependency-links`` is needed because currently cabby depends on `libtaxii <https://github.com/TAXIIProject/libtaxii>`_ trunk. This will be changed to a specific version with next release of `libtaxii`.

To install Cabby from source files: download a tarball, unpack it and install it manually with ``python setup.py install``.


Versioning
==========

Releases of cabby are given major.minor.revision version numbers, where major and minor correspond to the roadmap Intelworks has. The revision number is used to indicate a bug fix only release.


.. rubric:: Next steps

Continue with the :doc:`User guide <user>` to see how to use cabby.

.. vim: set spell spelllang=en:
