# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN mkdir -p /usr/share/fonts/truetype/freefont
RUN install -m644 FreeMonoBold.ttf /usr/share/fonts/truetype/freefont

# Install production dependencies.
RUN pip install --no-cache-dir .

#
CMD scrape-tweets beautiful_s2
