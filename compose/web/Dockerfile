FROM tiangolo/uwsgi-nginx-flask:flask
COPY ./web /app
RUN pip install -r /app/requirements.txt
WORKDIR /app

