==================
Installation guide
==================

.. highlight:: sh

This guide provides installation instructions for Cabby.


Build and install Cabby
=======================

You can automatically install the latest Cabby release from the `Python
Package Index <http://pypi.python.org/>`_ (PyPI) using ``pip``::

   (envname) $ pip install cabby

.. note::
    Since Cabby has `libtaxii <https://github.com/TAXIIProject/libtaxii>`_ as a dependency, the system libraries
    libtaxii requires needs to be installed. Check
    `libtaxii documentation <http://libtaxii.readthedocs.org/en/latest/installation.html#dependencies>`_ for the details.

To install Cabby from source files: download a tarball, unpack it and install it manually with ``python setup.py install``.


Versioning
==========

Releases of cabby are given major.minor.revision version numbers, where major and minor correspond to the roadmap Intelworks has. The revision number is used to indicate a bug fix only release.


.. rubric:: Next steps

Continue with the :doc:`User guide <user>` to see how to use cabby.

.. vim: set spell spelllang=en:
