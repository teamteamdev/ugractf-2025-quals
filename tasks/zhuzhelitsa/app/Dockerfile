FROM imachug/kyzylborda_lib
RUN apk add --no-cache zip && pip install gunicorn flask
WORKDIR /app
COPY . .
RUN zip static/bbcoin.zip client.py zhuzhelitsa.py
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:app"]
