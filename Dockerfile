FROM python:3.11-slim
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /andeschileong
WORKDIR /andeschileong
COPY . /andeschileong/

# RUN python manage.py collectstatic
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]