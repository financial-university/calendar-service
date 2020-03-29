FROM snakepacker/python:all AS builder

RUN python3.7 -m venv /usr/share/python3/app

ADD requirements*.txt /mnt/
RUN /usr/share/python3/app/bin/pip install -U pip setuptools

RUN apt-get update && \
    apt-get install python-dev

RUN /usr/share/python3/app/bin/pip install -Ur /mnt/requirements.txt && \
    /usr/share/python3/app/bin/pip check

FROM snakepacker/python:3.7 as app
COPY --from=builder /usr/share/python3/app /usr/share/python3/app

WORKDIR /mnt/
ADD calendar_fu /mnt/app/
#ADD start.py/ /mnt/
RUN ln -snf /usr/share/python3/app/bin/ /usr/bin/
ENV PATH="/usr/share/python3/app/bin:${PATH}"
ENV PYTHONPATH="/mnt/app"
RUN python -m app