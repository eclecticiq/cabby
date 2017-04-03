==========
User guide
==========

This user guide gives an overview of Cabby. It covers:

* using Cabby as a library
* using Cabby as a command line tool
* configuration via environment variables
* Docker quickstart guide

Note: this document assumes basic familiarity with TAXII specifications. Visit the `TAXII
homepage`_ for more information about its features.

.. _`TAXII homepage`: https://taxiiproject.github.io/


Using Cabby as a Python library
===============================

Below a few examples of how to use the Cabby in your code.
We use `test server <https://test.taxiistand.com/>`_ instance hosted by `TAXIIstand <https://www.taxiistand.com/>`_ in examples.

Create a client::

  from cabby import create_client

  client = create_client(
      'test.taxiistand.com',
      use_https=True,
      discovery_path='/read-write/services/discovery')

Discover advertised services::

  services = client.discover_services()
  for service in services:
      print('Service type={s.type}, address={s.address}'
            .format(s=service))

Poll content from a collection::

  content_blocks = client.poll(collection_name='all-data')

  for block in content_blocks:
      print(block.content)

Fetch the collections from Collection Management Serice (or Feed Management Service)::

  collections = client.get_collections(
      uri='https://test.taxiistand.com/read-write/services/collection-management')

Push content into Inbox Service::

  content = '<some>content-text</some>'
  binding = 'urn:stix.mitre.org:xml:1.1.1'

  client.push(
      content, binding, uri='/read-write/services/inbox/default')

To force client to use `TAXII 1.0 <taxii.mitre.org/specifications/version1.0/TAXII_Services_Specification.pdf>`_ specifications, initiate it with a specific ``version`` argument value::

  from cabby import create_client

  client = create_client('open.taxiistand.com', version='1.0')
  
.. note::
  Cabby client instances configured for TAXII 1.0 or TAXII 1.1 we will have slightly different method signatures (see :doc:`Cabby API documentation<api>` for details).


Authentication methods
----------------------

It is possible to set authentication parameters for TAXII requests::

  from cabby import create_client

  client = create_client(
      'secure.taxiiserver.com',
      discovery_path='/services/discovery')

  # basic authentication
  client.set_auth(username='john', password='p4ssw0rd')

  # or JWT based authentication
  client.set_auth(
      username='john',
      password='p4ssw0rd',
      jwt_auth_url='/management/auth'
  )

  # or basic authentication with SSL
  client.set_auth(
      username='john',
      password='p4ssw0rd',
      cert_file='/keys/ssl.cert',
      key_file='/keys/ssl.key'
  )

  # or only SSL authentication
  client.set_auth(
      cert_file='/keys/ssl.cert',
      key_file='/keys/ssl.key'
  )


Using Cabby as a command line tool
==================================

During installation Cabby adds a family of the command line tools prefixed with ``taxii-`` to your path:

.. highlight:: shell

Discover services::

  (venv) $ taxii-discovery \
                --host test.taxiistand.com \
                --path /read-only/services/discovery \
                --https

Fetch the collections list from Collection Management Service::

  (venv) $ taxii-collections \
               --path https://test.taxiistand.com/read-only/services/collection-management

Poll content from a collection (Polling Service will be autodiscovered in advertised services)::

  (venv) $ $ taxii-poll \
                 --host test.taxiistand.com \
                 --https --collection single-binding-slow \
                 --discovery /read-only/services/discovery

Push content into Inbox Service::

  (venv) $ taxii-push \
               --host test.taxiistand.com \
               --https \
               --discovery /read-write/services/discovery \
               --content-file /intel/stix/stuxnet.stix.xml \
               --binding "urn:stix.mitre.org:xml:1.1.1" \
               --subtype custom-subtype

Create a subscription::

  (venv) $ taxii-subscription \
               --host test.taxiistand.com \
               --https \
               --path /read-write/services/collection-management \
               --action subscribe \
               --collection collection-A

Fetch the collections from a service protected by Basic authentication::

  (venv) $ taxii-collections \
               --path https://test.taxiistand.com/read-write-auth/services/collection-management \
               --username test \
               --password test

Fetch the collections from a service protected by JWT authentication::

  (venv) $ taxii-collections \
               --host test.taxiistand.com \
               --https \
               --path /read-write-auth/services/collection-management \
               --username guest \
               --password guest \
               --jwt-auth /management/auth

Copy content blocks from one server to another::

  (venv) $ taxii-proxy \
               --poll-path https://open.taxiistand.com/services/poll \
               --poll-collection vxvault \
               --inbox-path https://test.taxiistand.com/read-write/services/inbox-stix \
               --inbox-collection stix-data \
               --binding urn:stix.mitre.org:xml:1.1.1

Use ``--help`` to get more usage details.

.. _configuration_via_env_vars:

Configuration via environment variables
=======================================

* ``CABBY_NO_HUGE_TREES``: by default Cabby enables support for huge trees in `lxml lib <http://lxml.de>`_ (see `lxml manual <http://lxml.de/parsing.html>`_). This disables security restrictions and enables support for very deep trees and very long text content. To disable this, set ``CABBY_NO_HUGE_TREES`` environment variable to any value.


Docker Quickstart
=================

To ease the threshold for trying out Cabby, it is possible to use the image provided by EclecticIQ:

.. code-block:: shell

    $ docker run cabby

Running this will execute the help script, giving you all the possible options:

.. code-block:: text

    Commands to be run:

        taxii-discovery
        taxii-poll
        taxii-collections
        taxii-push
        taxii-subscription
        taxii-proxy

    e.g. 
    
        $ docker run -ti cabby taxii-discovery \
              --host test.taxiistand.com \
              --use-https true \
              --path /read-write/services/discovery

    More information available at: http://cabby.readthedocs.org

    Or you can choose to drop back into a shell by providing `bash` as the command:

        $ docker run -ti cabby bash


.. rubric:: Next steps

See :doc:`Cabby API documentation<api>`.

.. vim: set spell spelllang=en:
