FROM ubuntu:focal as app
MAINTAINER sre@edx.org


# Packages installed:

# language-pack-en locales; ubuntu locale support so that system utilities have a consistent
# language and time zone.

# python; ubuntu doesnt ship with python, so this is the python we will use to run the application

# python3-pip; install pip to install application requirements.txt files

# libmysqlclient-dev; to install header files needed to use native C implementation for
# MySQL-python for performance gains.

# pkg-config; mysqlclient>=2.2.0 requires pkg-config (https://github.com/PyMySQL/mysqlclient/issues/620)

# libssl-dev; # mysqlclient wont install without this.

# python3-dev; to install header files for python extensions; much wheel-building depends on this

# gcc; for compiling python extensions distributed with python packages like mysql-client

# make; necessary to provision the container

# ENV variables for Python 3.12 support
ARG PYTHON_VERSION=3.12
ENV TZ=UTC
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive

# software-properties-common is needed to setup Python 3.12 env
RUN apt-get update && \
  apt-get install -y software-properties-common && \
  apt-add-repository -y ppa:deadsnakes/ppa

# If you add a package here please include a comment above describing what it is used for
RUN apt-get update && apt-get -qy install --no-install-recommends \
 build-essential \
 language-pack-en \
 locales \
 libmysqlclient-dev \
 pkg-config \
 libssl-dev \
 gcc \
 make \
 git \
 curl \
 python3-pip \
 python${PYTHON_VERSION} \
 python${PYTHON_VERSION}-dev \
 python${PYTHON_VERSION}-distutils 

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip setuptools
# delete apt package lists because we do not need them inflating our image
RUN rm -rf /var/lib/apt/lists/*

# need to use virtualenv pypi package with Python 3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION}
RUN pip install virtualenv

# Create virtual environment with Python 3.12
ENV VIRTUAL_ENV=/edx/venvs/edx-exams
RUN virtualenv -p python${PYTHON_VERSION} $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# python is python3
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV DJANGO_SETTINGS_MODULE edx_exams.settings.production

EXPOSE 18740
RUN useradd -m --shell /bin/false app

WORKDIR /edx/app/edx-exams

# Copy the requirements explicitly even though we copy everything below
# this prevents the image cache from busting unless the dependencies have changed.
COPY requirements/production.txt /edx/app/edx-exams/requirements/production.txt

# Dependencies are installed as root so they cannot be modified by the application user.
RUN pip install -r requirements/production.txt

RUN mkdir -p /edx/var/log

# Code is owned by root so it cannot be modified by the application user.
# So we copy it before changing users.
USER app

# Gunicorn 19 does not log to stdout or stderr by default. Once we are past gunicorn 19, the logging to STDOUT need not be specified.
CMD gunicorn --workers=2 --name edx-exams -c /edx/app/edx-exams/edx_exams/docker_gunicorn_configuration.py --log-file - --max-requests=1000 edx_exams.wsgi:application

# This line is after the requirements so that changes to the code will not
# bust the image cache
COPY . /edx/app/edx-exams
