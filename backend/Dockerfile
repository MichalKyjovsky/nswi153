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
RUN flake8 --ignore=E501,F401,W293,F541,E266 /usr/src/backend/crawler

# Install Python dependencies
RUN pip pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/backend/wheels /usr/src/backend/crawler/requirements.txt


###########################################
################## FINAL ##################
###########################################

# Use the latest Python image
FROM python:3

# Create a directory for application user
RUN mkdir -p /home/crawler

# Create the application user
RUN addgroup --system app
RUN adduser --system --group app

# Create the appropriate directories
ENV HOME=/home
ENV APP_HOME=/home/crawler
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/backend/wheels /wheels
COPY --from=builder /usr/src/backend/crawler/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# Copy the entire project
COPY ./crawler $APP_HOME

# Chown all the files to the app user
RUN chown -R app:app $HOME

#Change to the app user
USER app
