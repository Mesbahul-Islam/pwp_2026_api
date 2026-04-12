FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/app

COPY requirements.txt /opt/app/requirements.txt
RUN pip install --no-cache-dir -r /opt/app/requirements.txt

COPY . /opt/app
RUN mkdir -p /opt/app/data \
    && chgrp -R root /opt/app \
    && chmod -R g=u /opt/app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn eyesedge.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120"]
