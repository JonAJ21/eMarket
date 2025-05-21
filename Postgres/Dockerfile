FROM postgres:15

RUN apt update && \
    apt install -y postgresql-server-dev-15 make gcc wget libicu-dev

RUN wget https://github.com/pgbigm/pg_bigm/archive/refs/tags/v1.2-20240606.tar.gz && \
    tar zxf v1.2-20240606.tar.gz && \
    cd pg_bigm-1.2-20240606 && \
    make USE_PGXS=1 && \
    make USE_PGXS=1 install && \
    cd .. && \
    rm -rf pg_bigm-1.2-20240606 v1.2-20240606.tar.gz


COPY init-extensions.sql /docker-entrypoint-initdb.d/