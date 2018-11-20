# dockerfile for running tests in jenkins etc.
FROM python:3-slim-stretch
LABEL maintainer="EclecticIQ <cabby@eclecticiq.com>"
RUN python3 -m venv --system-site-packages /venv
ENV PATH=/venv/bin:$PATH

COPY ./requirements.txt ./requirements-dev.txt /cabby
RUN pip install -r /cabby/requirements-dev.txt
COPY . /cabby
RUN pip install -e /cabby

COPY ./docker-help.sh /
RUN sh -c "cat /docker-help.sh >> /root/.bashrc"
CMD ["/docker-help.sh"]
