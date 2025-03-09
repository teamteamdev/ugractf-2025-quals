FROM imachug/kyzylborda_lib
RUN apk add --no-cache chromium-chromedriver
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["./start.sh"]
