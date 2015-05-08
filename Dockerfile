# Set the base image to Python
FROM python:2.7.9
MAINTAINER Intelworks <opentaxii@intelworks.com>

# Volume for possible input
VOLUME [ "/input" ]

# Create the working dir and set the working directory
WORKDIR /

# Requirements
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt \
    && rm -f requirements.txt

# Install Cabby
RUN mkdir /cabby
COPY ./ /cabby
RUN cd /cabby \
    && python setup.py install \
    && rm -rf /cabby

# Helper
COPY docker/help.sh /help.sh

# Give help, unless command is given
CMD [ "/help.sh" ]

