taxii-client
============

A simple python client for TAXII server.

## Installation
```shell
pip install git+ssh://github.com/Intelworks/taxii-client.git
```

## Usage

```python
from taxii_client import create_client

client = create_client('taxiitest.mitre.org', port=80)


for service in client.discover_services(uri='/services/discovery'):
    print service.to_text()


# if only one POLL service advertised, client will use it automatically
content_blocks = client.poll('default')

for block in content_blocks:
    print block['content']


content = '<some>content-text</some>'
binding = 'urn:stix.mitre.org:xml:1.1.1'

# it is also possible to specify a path to a service
client.push(content, binding, uri='/services/inbox/default')


```


## Scripts

Usage:
```shell

$ python bin/taxii-discovery --host taxiitest.mitre.org

$ python bin/taxii-poll --host taxiitest.mitre.org --collection default --dest-dir /tmp/

$ python bin/taxii-push --host taxiitest.mitre.org --file /tmp/samples/stix/watchlist-1.1.1.xml

```

Use ```--help``` to get more usage details

