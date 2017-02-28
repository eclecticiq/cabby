cabby
=====

Python TAXII client implementation from `EclecticIQ <https://www.eclecticiq.com>`_.

:Source: https://github.com/EclecticIQ/cabby
:Documentation: http://cabby.readthedocs.org
:Information: https://www.eclecticiq.com
:Download: https://pypi.python.org/pypi/cabby/

|travis badge| |landscape.io badge| |coveralls.io badge| |version badge| |py.version badge| |downloads badge| |license badge| |docs badge|

.. |travis badge| image:: https://travis-ci.org/EclecticIQ/cabby.svg?branch=master
   :target: https://travis-ci.org/EclecticIQ/cabby
   :alt: Build Status
.. |landscape.io badge| image:: https://landscape.io/github/EclecticIQ/cabby/master/landscape.svg?style=flat
   :target: https://landscape.io/github/EclecticIQ/cabby/master
   :alt: Code Health
.. |coveralls.io badge| image:: https://coveralls.io/repos/EclecticIQ/cabby/badge.svg
   :target: https://coveralls.io/r/EclecticIQ/cabby
   :alt: Coverage Status
.. |version badge| image:: https://pypip.in/version/cabby/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/cabby/ 
.. |py.version badge| image:: https://pypip.in/py_versions/cabby/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/cabby/ 
.. |downloads badge| image:: https://pypip.in/download/cabby/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/cabby/
.. |license badge| image:: https://pypip.in/license/cabby/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/cabby/
.. |docs badge| image:: https://readthedocs.org/projects/cabby/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/cabby/

A simple Python library for interacting with TAXII servers.


Docker
--------

From version 0.1.13, the docker image is based on 'Alpine' linux. This means the size of the Image was reduced from 311MB to 74MB

To run cabby using docker, execute the following:

  docker run --rm=true eclecticiq/cabby:latest taxii-discovery --path https://test.taxiistand.com/read-only/services/discovery

Feedback
--------

You are encouraged to provide feedback by commenting on open issues or sending us 
email at cabby@eclecticiq.com

