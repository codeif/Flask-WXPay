FROM codeif/pipenv-example

COPY . /app

WORKDIR /app/example

RUN pipenv sync

ENV FLASK_ENV=development FLASK_APP=demo

EXPOSE 5000

CMD ["pipenv", "run", "flask", "run", "-h", "0.0.0.0"]
