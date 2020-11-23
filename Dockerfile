FROM balenalib/raspberrypi3-debian-python:3.7.9-buster

LABEL maintainer="James Wong <jingw222@gmail.com>"

ARG DEBIAN_FRONTEND=noninteractive

ENV LC_ALL=C.UTF-8 \
  LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1

# Install dependencies
RUN apt-get update && \
  apt-get install --no-install-recommends -y build-essential cmake pkg-config apt-utils && \
  apt-get install --no-install-recommends -y libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libilmbase23 libopenexr-dev libgtk-3-dev && \
  apt-get install --no-install-recommends -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev && \
  apt-get install --no-install-recommends -y libxvidcore-dev libx264-dev && \
  apt-get install --no-install-recommends -y gnupg2 apt-transport-https curl libatlas-base-dev gfortran python3-dev libpq-dev

# Add Coral Edge TPU package repository 
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add

# Install the Edge TPU runtime
# Note:
# If you need maximum performance, install `libedgetpu1-legacy-max` instead. 
# Check out the documentation for more. 
RUN apt-get update && apt-get install -y libedgetpu1-legacy-std

# Add pip package index urls
RUN echo '[global]' >> /etc/pip.conf && \
  echo 'index-url = https://www.piwheels.org/simple' >> /etc/pip.conf && \
  echo 'extra-index-url = https://pypi.python.org/simple' >> /etc/pip.conf 

WORKDIR /hiitpi

COPY hiitpi hiitpi
COPY migrations migrations
COPY app.py boot.sh requirements.txt ./

RUN pip install --upgrade pip && \
  pip install --upgrade setuptools wheel && \
  pip install pysocks && \
  pip install -r requirements.txt

RUN chmod +x boot.sh 

EXPOSE 8050

ENTRYPOINT ["./boot.sh"]
