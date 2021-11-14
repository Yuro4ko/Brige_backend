FROM python:3

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir /web
COPY . /web/
WORKDIR /web

RUN pip install --upgrade pip
RUN pip install flask
RUN pip install flask_sqlalchemy

ENTRYPOINT ["python", "app.py"]
CMD ["runserver", "0.0.0.0:8000"]