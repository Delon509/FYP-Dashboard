FROM python:3.7-slim
COPY dashrequirement.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
CMD gunicorn -b 0.0.0.0:80 index:server