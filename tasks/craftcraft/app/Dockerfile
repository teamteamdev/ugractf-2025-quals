FROM python:alpine
RUN pip install quart uvicorn && mkdir /state
COPY . /app
WORKDIR /app
EXPOSE 3001
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "3001", "--workers", "1", "server:app"]
