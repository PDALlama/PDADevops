FROM postgres:12.20

RUN apt update
RUN apt install openssh-server -y

RUN service ssh start

COPY init.sh /docker-entrypoint/
RUN chmod +x /docker-entrypoint/init.sh

ENTRYPOINT ["/docker-entrypoint/init.sh"]
CMD ["su", "postgres", "-c", "exec postgres"]