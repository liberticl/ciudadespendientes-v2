FROM python:3.11-slim
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /andeschileong
WORKDIR /andeschileong
COPY . /andeschileong/

RUN python manage.py collectstatic --noinput

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "andeschileong.wsgi:application"]
CMD ["python", "manage.py", "runserver"]