FROM scratch
COPY --from=alpine /bin/busybox /bin/sh
COPY --from=alpine /lib/ld-musl-x86_64.so.1 /lib/
COPY --from=alpine /var/empty /etc
USER 1000:1000
CMD ["/bin/sh", "-i"]
