FROM alpine:3.6

COPY . /app
WORKDIR /app

#RUN apk add --update --no-cache \
RUN apk add --no-cache \
    python \
    python-dev \
    py-pip \
    musl-dev \
    gcc \
    postgresql-dev \
  && pip install pipenv \
  && pipenv install \
  && pipenv run python manage.py migrate

EXPOSE 8000
CMD ["pipenv", "run", "python manage.py runserver"]
