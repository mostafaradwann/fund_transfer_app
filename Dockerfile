FROM python:3.8

WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y libsqlite3-dev
RUN pip install -r requirments.txt
EXPOSE 9000
CMD ["python", "main.py"]