FROM snakepacker/python:all AS builder

RUN python3.8 -m venv /usr/share/python3/app

RUN /usr/share/python3/app/bin/pip install -U pip setuptools wheel

RUN apt-get update && \
    apt-get install python-dev

WORKDIR /temp/

COPY setup.py requirements*.txt MANIFEST.in README.md ./
COPY calendar_fu ./calendar_fu

RUN /usr/share/python3/app/bin/python setup.py sdist bdist_wheel

RUN /usr/share/python3/app/bin/pip install -U ./dist/calendar_fu*.whl

FROM snakepacker/python:3.8 as app
COPY --from=builder /usr/share/python3/app /usr/share/python3/app

RUN ln -snf /usr/share/python3/app/bin/ /usr/bin/
ENV PATH="/usr/share/python3/app/bin:${PATH}"
ENV PYTHONPATH="/mnt/app"
CMD ["calendar_fu"]