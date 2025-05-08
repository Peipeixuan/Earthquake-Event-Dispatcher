FROM prom/prometheus

# copy the Prometheus configuration file
COPY ./prometheus.yml /etc/prometheus/prometheus.yml

# expose the Prometheus server port
EXPOSE 9090

# set the entrypoint command
ENTRYPOINT [ "prometheus", \
             "--config.file=/etc/prometheus/prometheus.yml", \
             "--web.external-url=/prometheus/", \
             "--web.route-prefix=/", \
             "--log.level=info", \
             "--log.format=logger:stderr" ]