#!/bin/sh

_cmd=""
if [ $0 = '/cabby/docker-help.sh' ]; then
	_cmd="docker run -it eclecticiq/cabby "
fi

cat <<EOF

Cabby commands you can run:

  taxii-collections
  taxii-discovery
  taxii-poll
  taxii-proxy
  taxii-push
  taxii-subscriptions
EOF

echo
echo "For example: ${_cmd}taxii-discovery --path https://test.taxiistand.com/read-write/services/discovery"
echo
echo "More information available at: http://cabby.readthedocs.org"
echo

unset _cmd
