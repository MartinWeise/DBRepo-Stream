FROM python:3.9
COPY ./main.py /home/main.py
COPY ./requirements.txt /home/requirements.txt
WORKDIR /home
RUN pip3 install -r requirements.txt
CMD [ "python3", "./main.py" ]