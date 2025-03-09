FROM imachug/kyzylborda_lib
RUN pip install gunicorn
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:app"]
