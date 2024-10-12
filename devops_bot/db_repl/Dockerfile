FROM postgres:12.20

COPY init.sh /docker-entrypoint/
RUN chmod +x /docker-entrypoint/init.sh

ENTRYPOINT ["/docker-entrypoint/init.sh"]

CMD ["su", "postgres", "-c", "exec postgres"]