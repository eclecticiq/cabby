==================
Installation guide
==================

.. highlight:: sh

Install Python
==============

OpenTAXII works with both latest Python version (3.4) and version 2.7. You can install Python with your operating system’s package manager or download it directly `here <http://www.python.org/download/>`_.

You can verify that Python is installed by typing ``python`` from your shell; you should see something like::

    $ python
    Python 2.7.8 (default, Oct 19 2014, 16:02:00)
    [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.54)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 

Install Cabby
=============

To sandbox the project and protect system-wide python it is recommended to install Cabby into a `virtual environment <https://virtualenv.pypa.io/en/latest/installation.html>`_ (*virtualenv*):

Create a virtual environment named venv::

   $ virtualenv venv

Where ``venv`` is a directory to place the new environment.

Activate this environment::

   $ . venv/bin/activate
   (venv) $
   
You can now install the latest Cabby release from the `Python Package Index <http://pypi.python.org/>`_ (PyPI) using ``pip``::

   (venv) $ pip install cabby

.. note::
    Since Cabby has `libtaxii <https://github.com/TAXIIProject/libtaxii>`_ as a dependency, the system libraries
    `libtaxii` requires need to be installed. Check
    `libtaxii documentation <http://libtaxii.readthedocs.org/en/latest/installation.html#dependencies>`_ for the details.

To install Cabby from source files: download a tarball, unpack it and install it manually with ``python setup.py install``.


Versioning
==========

Releases of Cabby are given major.minor.revision version numbers, where major and minor correspond to the roadmap EclecticIQ has. The revision number is used to indicate a bug fix only release.


.. rubric:: Next steps

Continue with the :doc:`User guide <user>` to see how to use Cabby.

.. vim: set spell spelllang=en:
