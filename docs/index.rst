=====
Cabby
=====

Cabby is Python TAXII client implementation from Intelworks.

TAXII (Trusted Automated eXchange of Indicator Information) is a collection of specifications defining a set of services and message exchanges used for sharing cyber threat intelligence information between parties. Check `TAXII homepage <http://taxii.mitre.org/>`_ to get more information.


Cabby is designed from the ground up to act as a Python library and as a command line tool, it's key features are:

* **Rich feature set**:
  it supports all TAXII services according to TAXII specification (v1.0 and v1.1).

* **Version agnostic**:
  it abstracts specific implementation details and returns version agnostic entities.

* **Stream parsing**:
  Heavy TAXII Poll Response messages are parsed on the fly, reducing memory footprint and time untill first content block is available.


.. rubric:: Documentation contents

.. toctree::
   :maxdepth: 1

   installation
   user
   api
   developer
   changes
   license

.. rubric:: External links

* `Online documentation <https://cabby.readthedocs.org/>`_ (Read the docs)
* `Project page <https://github.com/Intelworks/cabby/>`_ with source code and issue tracker (Github)
* `Python Package Index (PyPI) page <http://pypi.python.org/pypi/cabby/>`_ with released tarballs
