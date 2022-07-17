###########################################
################# BUILDER #################
###########################################

# Use the latest Python image
FROM python:3 as builder

# Set the working directory to /usr/src/app
WORKDIR /usr/src/backend/crawler

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install flake8

# Copy the current directory contents into the container at /usr/src/backend/crawler
COPY ./crawler /usr/src/backend/crawler

# Run the code analysis
# RUN flake8 --ignore=E501,F401,W293,F541,E266,F405,F403,W503 /usr/src/backend/crawler

# Install Python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/backend/wheels -r /usr/src/backend/crawler/requirements.txt


###########################################
################## FINAL ##################
###########################################

# Use the latest Python image
FROM python:3

# Create a directory for application user
RUN mkdir -p /home/backend

# Create the application user
RUN addgroup --system app
RUN adduser --system --group app

# Create the appropriate directories
ENV HOME=/home/backend
ENV APP_HOME=/home/backend/crawler
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install dependencies
RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  && apt-get install -y --no-install-recommends netcat \
    # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/backend/wheels /wheels
COPY --from=builder /usr/src/backend/crawler/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# Copy the entire project
COPY ./crawler $APP_HOME

COPY ./entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./start.sh /start.sh
RUN sed -i 's/\r$//g' /start.sh
RUN chmod +x /start.sh

COPY ./celery/worker/start.sh /start-celeryworker.sh
RUN sed -i 's/\r$//g' /start-celeryworker.sh
RUN chmod +x /start-celeryworker.sh

COPY ./celery/beat/start.sh /start-celerybeat.sh
RUN sed -i 's/\r$//g' /start-celerybeat.sh
RUN chmod +x /start-celerybeat.sh

COPY ./celery/flower/start.sh /start-flower.sh
RUN sed -i 's/\r$//g' /start-flower.sh
RUN chmod +x /start-flower.sh

# Chown all the files to the app user
RUN chown -R app:app $HOME

#Change to the app user
USER app

ENTRYPOINT ["/entrypoint.sh"]
