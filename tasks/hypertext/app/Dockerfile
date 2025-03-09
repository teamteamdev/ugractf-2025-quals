FROM alpine
RUN apk add coreutils bash file socat
WORKDIR /app/source
CMD ["socat", "unix-listen:/tmp/app.sock,mode=0666,fork", "exec:/app/source/server"]
