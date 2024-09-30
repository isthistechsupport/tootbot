# syntax=docker/dockerfile:1
FROM python:3.10.9-alpine
WORKDIR /app
COPY ["*.py", "requirements.txt", "./"]
RUN pip3 install -r requirements.txt
CMD [ "python3", "-u", "tootbot.py" ]
