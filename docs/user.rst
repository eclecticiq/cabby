==========
User guide
==========

This user guide gives an overview of Cabby. It covers:

* Using Cabby as a Python library and
* Using Cabby as a command line tool

Note: this document assumes basic familiarity with TAXII specification; visit the `TAXII
homepage`_ for more information about its features.

.. _`TAXII homepage`: http://taxii.mitre.org/


Using Cabby as a Python library
===============================

.. code-block:: python

  from cabby import create_client

  client = create_client('taxiitest.mitre.org', port=80)

  for service in client.discover_services(uri='/services/discovery'):
      print(service.to_text())

  # if only one POLL service advertised, client will use it automatically
  content_blocks = client.poll('default')

  for block in content_blocks:
      print(block['content'])

  content = '<some>content-text</some>'
  binding = 'urn:stix.mitre.org:xml:1.1.1'

  # it is also possible to specify a path to a service
  client.push(content, binding, uri='/services/inbox/default')

Using Cabby as a command line tool
==================================

.. code-block:: console

  $ taxii-discovery --host taxiitest.mitre.org

  $ taxii-poll --host taxiitest.mitre.org --collection default --dest-dir /tmp/

  $ taxii-push --host taxiitest.mitre.org --file /tmp/samples/stix/watchlist-1.1.1.xml

Use ``--help`` to get more usage details.


.. rubric:: Next steps

The user guide should be enough to get you started with Cabby.

.. vim: set spell spelllang=en:
