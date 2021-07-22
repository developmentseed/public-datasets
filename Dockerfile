FROM tiangolo/uvicorn-gunicorn:python3.8

ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN git clone https://github.com/stac-utils/stac-fastapi\
    && pip install stac-fastapi/stac_fastapi/api \
    && pip install stac-fastapi/stac_fastapi/types \
    && pip install stac-fastapi/stac_fastapi/extensions \
    && pip install stac-fastapi/stac_fastapi/pgstac

COPY public_datasets/ /tmp/public_datasets/
RUN pip install /tmp/public_datasets/extensions /tmp/public_datasets/api
RUN rm -rf /tmp/public_datasets


