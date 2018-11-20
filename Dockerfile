FROM python:3-slim-stretch
LABEL maintainer="EclecticIQ <cabby@eclecticiq.com>"
RUN python3 -m venv --system-site-packages /venv
ENV PATH=/venv/bin:$PATH

COPY ./requirements.txt ./requirements-dev.txt /cabby
RUN pip install -r /cabby/requirements-dev.txt
COPY . /cabby
RUN pip install -e /cabby

RUN sh -c "cat /cabby/docker-help.sh >> /root/.bashrc"
CMD ["/cabby/docker-help.sh"]
