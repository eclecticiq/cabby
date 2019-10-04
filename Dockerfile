FROM python:3-slim-stretch
LABEL maintainer="EclecticIQ <cabby@eclecticiq.com>"

COPY . /cabby/
RUN pip install -r /cabby/requirements-dev.txt && \
    pip install -e /cabby && \
    cat /cabby/docker-help.sh >> /root/.bashrc

CMD ["/cabby/docker-help.sh"]
