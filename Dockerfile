FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    binutils libproj-dev gdal-bin gettext \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR $APP_HOME

# ES lint
RUN pip install --upgrade pip
RUN pip install flake8

# Install Python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir $APP_HOME/wheels -r requirements.txt

# Copy project files
COPY . .
RUN flake8 --exclude .
RUN pip install --no-cache $APP_HOME/wheels/*

# Create logs file
RUN mkdir logs
RUN touch logs/debug.log

# Setup wait-for-database script
RUN chmod +x .docker/wait-for-it.sh

# Entrypoint script to wait for database
# CMD ["/bin/bash", "-c", ".docker/wait-for-it.sh eneo-db:${POSTGRES_PORT} -- python manage.py migrate && python manage.py collectstatic --no-input --clear && gunicorn ona.wsgi:application --bind 0.0.0.0:8000 && python manage.py loaddata fixtures/config.json && python manage.py loaddata fixtures/user.json && python manage.py itinary && python manage.py ona_import && python manage.py dry_import && python manage.py drc_import && python manage.py drnea_import"]
CMD ["/bin/bash", "-c", ".docker/wait-for-it.sh eneo-db:${POSTGRES_PORT} -- python manage.py migrate && python manage.py collectstatic --no-input --clear && python manage.py loaddata fixtures/config.json && python manage.py loaddata fixtures/user.json && gunicorn ona.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 36000"]
# CMD ["/bin/bash", "-c", ".docker/wait-for-it.sh eneo-db:${POSTGRES_PORT} -- python manage.py migrate && python manage.py collectstatic --no-input --clear && gunicorn ona.wsgi:application --bind 0.0.0.0:8000 && python manage.py loaddata fixtures/config.json && python manage.py loaddata fixtures/user.json && python manage.py itinary"]
