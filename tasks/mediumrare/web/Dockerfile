FROM imachug/kyzylborda_lib
RUN pip install gunicorn
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# sqlmap hangs with a single worker
CMD ["gunicorn", "-w", "16", "-b", "unix:/tmp/app.sock", "server:app"]
