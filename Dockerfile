FROM python:3.11-slim
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /andeschileong
WORKDIR /andeschileong
COPY . /andeschileong/

CMD ["python", "manage.py", "runserver"]