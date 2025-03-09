FROM imachug/kyzylborda_lib
RUN pip install flask gunicorn
WORKDIR /app
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:app"]
