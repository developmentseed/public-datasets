FROM tiangolo/uvicorn-gunicorn:python3.8

ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN pip install stac-fastapi.api~=2.0 stac-fastapi.types~=2.0 stac-fastapi.extensions~=2.0 stac-fastapi.pgstac~=2.0

COPY public_datasets/ /tmp/public_datasets/
RUN pip install /tmp/public_datasets/extensions /tmp/public_datasets/api
RUN rm -rf /tmp/public_datasets


