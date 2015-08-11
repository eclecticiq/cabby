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

Fetch the collections from Collection Management Serice (or Feed Management Service)::

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


Authentication methods
======================
It is possible to set authentication parameters for TAXII requests::

  from cabby import create_client

  client = create_client('taxii.example.com', discovery_path='/services/discovery')

  # basic authentication
  client.set_auth(username='client', password='password')

  # JWT based authentication
  client.set_auth(
      username='client',
      password='password',
      jwt_auth_url='/management/auth'
  )

  # basic authentication with SSL
  client.set_auth(
      username='client',
      password='password',
      cert_file='/tmp/ssl.cert',
      key_file='/tmp/ssl.key'
  )

  # only SSL authentication
  client.set_auth(
      cert_file='/tmp/ssl.cert',
      key_file='/tmp/ssl.key'
  )


Using Cabby as a command line tool
==================================

During installation Cabby adds a family of the command line tools prefixed with ``taxii-`` to your path:

.. highlight:: shell

Discover services::

  (venv) $ taxii-discovery --host taxiitest.mitre.org --path /services/discovery/

Poll content from a collection (Polling Service autodiscovered in advertised services)::

  (venv) $ taxii-poll --host taxiitest.mitre.org --collection default --discovery /services/discovery/

Fetch the collections list from Collection Management Service::

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


Fetch the collections from a service protected by Basic authentication::

  (venv) $ taxii-collections --path https://taxii.example.com/services/collections \
                             --username test \
                             --password test

Fetch the collections from a service protected by JWT authentication::

  (venv) $ taxii-collections --host taxii.example.com
                             --path /services/collections \
                             --username test \
                             --password test \
                             --jwt-auth /management/auth

Use ``--help`` to get more usage details.

Docker Quickstart
=================

To ease the threshold for trying out cabby, it is possible to use the Intelworks provided image.

.. code-block:: shell

    docker run cabby

Running this will execute the help script, giving you all the possible options:

.. code-block:: text

     Commands to be run:

        taxii-discovery
        taxii-poll
        taxii-collections
        taxii-push
        taxii-subscription

        e.g. docker run -ti cabby taxii-discovery --host taxxii.server --path /services/discovery

    More information available at: http://cabby.readthedocs.org

    Or you can choose to drop back into a shell by providing: bash as the command:

        docker run -ti cabby bash



.. rubric:: Next steps

See :doc:`Cabby API documentation<api>`.

.. vim: set spell spelllang=en:
