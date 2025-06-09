# Base docker image
FROM huggingface/transformers-pytorch-gpu:4.22.1 as base

WORKDIR /app

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip install pip --upgrade
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python

ENV PYTHONPATH /app
COPY . .

CMD [ "bash" ]
