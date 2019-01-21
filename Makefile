build:
	docker build -t flask-wxpay .

run:
	docker run -v $(pwd):/app -p 5000:5000 flask-wxpay

bash:
	docker run -it -v $(pwd):/app flask-wxpay /bin/bash
