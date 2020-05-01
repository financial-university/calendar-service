format:
    black calendar_fu

build:
    python setup.py sdist bdist_wheel

run:
    python -m calendar_fu -D --file