FROM python:3.11-slim
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /andeschileong
WORKDIR /andeschileong
COPY . /andeschileong/

RUN apt-get update && apt-get install -y nginx
RUN mkdir -p /andeschileong/static
COPY nginx.conf /etc/nginx/nginx.conf
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput --clear
RUN nginx -t

EXPOSE 80

CMD service nginx start && gunicorn --workers 3 andeschileong.wsgi:application --bind 0.0.0.0:8000 --log-level debug