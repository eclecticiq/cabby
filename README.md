taxii-client
============

TAXII python client

A simple python client for TAXII servers. Usage:

```python
from taxii_client import create_client

client = create_client('taxiitest.mitre.org', port=80)


# client will use default discovery path
for service in client.discover_services(uri='/services/discovery'):
    print service.to_text()


# if only one POLL service advertised, client will use it automatically
content_blocks = client.poll('default')

for block in content_blocks:
    print block['content']

```

