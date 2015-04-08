==========
User guide
==========

This user guide gives an overview of Cabby. It covers using Cabby as a:

* Python library
* command line tool

Note: this document assumes basic familiarity with TAXII specifications. Visit the `TAXII
homepage`_ for more information about its features.

.. _`TAXII homepage`: http://taxii.mitre.org/


Using Cabby as a Python library
===============================

Below a few examples of how to use the Cabby in your code.

Create a client::

  from cabby import create_client

  client = create_client('taxiitest.mitre.org', discovery_path='/services/discovery')

Discover advertised services::

  services = client.discover_services()
  for service in services:
      print 'Service type={s.type}, address={s.address}'.format(s=service)

Poll content from a collection::

  content_blocks = client.poll(collection_name='default')

  for block in content_blocks:
      print block.content

Fetch collections from Collection Management Serice (or Feed Management Service)::

  collections = client.get_collections(uri='https://example.com/collection-management-service')

Push content into Inbox Service::

  content = '<some>content-text</some>'
  binding = 'urn:stix.mitre.org:xml:1.1.1'

  client.push(content, binding, uri='/services/inbox/default')

To force client to use `TAXII 1.0 <taxii.mitre.org/specifications/version1.0/TAXII_Services_Specification.pdf>`_ specifications, initiate it with a specific ``version`` argument value::

  from cabby import create_client

  client = create_client('hailataxii.com', version='1.0')

.. note::
	Cabby client instances configured for TAXII 1.0 or TAXII 1.1 we will have slightly different method signatures (see :doc:`Cabby API documentation<api>` for details).

Using Cabby as a command line tool
==================================

During installation Cabby adds a family of the command line tools prefixed with ``taxii-`` to your path:

.. highlight:: shell

Discover services::

  (venv) $ taxii-discovery --host taxiitest.mitre.org --path /services/discovery/

Poll content from a collection (Polling Service autodiscovered in advertised services)::

  (venv) $ taxii-poll --host taxiitest.mitre.org --collection default --discovery /services/discovery/

Fetch collections list from Collection Management Service::

  (venv) $ taxii-collections --path https://taxii.example.com/services/collection-management

Push content into Inbox Service::

  (venv) $ taxii-push --host taxiitest.mitre.org \
               --discovery /services/discovery \
               --content-file /tmp/stuxnet.stix.xml \
               --binding "urn:stix.mitre.org:xml:1.1.1" \
               --subtype custom-subtype

Create a subscription::

  (venv) $ taxii-subscription --host taxii.example.com \
                       --https \
                       --path /services/collection-management \
                       --action subscribe \
                       --collection collection-A

Use ``--help`` to get more usage details.


.. rubric:: Next steps

See :doc:`Cabby API documentation<api>`.

.. vim: set spell spelllang=en:
