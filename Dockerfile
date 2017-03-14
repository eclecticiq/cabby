# Set the base image to Python
FROM alpine:3.4
MAINTAINER EclecticIQ <cabby@eclecticiq.com>

# Volume for possible input
VOLUME [ "/input" ]

# Create the working dir and set the working directory
WORKDIR /

# Setup Python
RUN apk add --no-cache -U \
      ca-certificates \
      build-base \
      libxml2 \
      libxml2-dev \
      libxslt \
      libxslt-dev \
      make \
      python-dev \
      py-pip \
      python \
    && pip install --upgrade pip setuptools  


# Setup Requirements
COPY ./ /cabby
RUN pip install -r /cabby/requirements.txt \
  && cd /cabby \
  && python setup.py install 
  
# Cleanup
RUN apk del build-base \
      libxml2-dev \
      libxslt-dev \
      python-dev \
      build-base \
    && rm -rf /var/cache/apk/*  \
    && rm -r /root/.cache \
    && rm -f requirements.txt \
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
        echo 'e.g. docker run -ti eclecticiq/cabby taxii-discovery --path https://test.taxiistand.com/read-write/services/discovery';\
        echo '';\
        echo 'More information available at: http://cabby.readthedocs.org';\
        echo 'Or you can choose to drop back into a shell by providing: bash as the command:';\
        echo '';\
        echo 'docker run -ti cabby bash"'; }  > /help.sh  && chmod 750 /help.sh

# Give help, unless command is given
CMD [ "/help.sh" ]

