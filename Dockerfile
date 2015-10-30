# Set the base image to Python
FROM python:2.7.9
MAINTAINER Intelworks <opentaxii@intelworks.com>

# Volume for possible input
VOLUME [ "/input" ]

# Create the working dir and set the working directory
WORKDIR /

# Requirements
COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -f requirements.txt

# Install Cabby
RUN mkdir /cabby
COPY ./ /cabby
RUN cd /cabby \
    && python setup.py install \
    && rm -rf /cabby

RUN {   echo '#!/bin/sh';\
        echo 'echo "';\
        echo ' Commands to be run:';\
        echo '      taxii-discovery ';\
        echo '      taxii-poll';\
        echo '      taxii-collections';\
        echo '      taxii-push ';\
        echo '      taxii-subscription';\
        echo '      taxii-proxy';\
        echo '';\
        echo 'e.g. docker run -ti intelworks/cabby taxii-discovery --path https://test.taxiistand.com/read-write/services/discovery';\
        echo '';\
        echo 'More information available at: http://cabby.readthedocs.org';\
        echo 'Or you can choose to drop back into a shell by providing: bash as the command:';\
        echo '';\
        echo 'docker run -ti cabby bash"'; }  > /help.sh  && chmod 750 /help.sh

# Give help, unless command is given
CMD [ "/help.sh" ]

