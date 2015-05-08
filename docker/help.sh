#!/bin/bash

echo "
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
"
