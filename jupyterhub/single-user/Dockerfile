FROM jupyter/scipy-notebook:latest
COPY requirements.txt /home/requirements.txt
RUN pip3 install -r /home/requirements.txt
RUN pip3 install --no-cache jupyterhub