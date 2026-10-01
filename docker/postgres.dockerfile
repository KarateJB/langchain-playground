FROM postgres:18.3

RUN mkdir -p /tmp/pgp_keys

COPY postgres/create_db.sql /docker-entrypoint-initdb.d/create_db.sql
COPY postgres/create_extensions.sql /docker-entrypoint-initdb.d/create_extensions.sql
COPY postgres/run_psql.sh /usr/local/bin/
COPY postgres/docker-entrypoint.sh /usr/local/bin/

RUN apt-get update \
    && apt-get install -y sudo \
    && apt-get install -y pgagent \
    && apt-get install -y dos2unix

RUN dos2unix /usr/local/bin/docker-entrypoint.sh \
    && dos2unix /usr/local/bin/run_psql.sh

RUN sudo adduser postgres sudo
RUN ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
