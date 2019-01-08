FROM codeif/pipenv-example
# FROM flask-wxpay

COPY . /app

WORKDIR /app/example

RUN pipenv sync

ENV TZ=Asia/Shanghai
ENV FLASK_ENV=development FLASK_APP=demo

EXPOSE 5000

CMD ["pipenv", "run", "flask", "run", "-h", "0.0.0.0"]
