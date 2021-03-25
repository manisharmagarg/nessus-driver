FROM ubuntu:16.04
RUN apt-get update && apt-get install -y \
curl
RUN apt-get install -y python-pip python-dev build-essential
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
RUN dpkg -i /chrome.deb || apt-get install -yf
RUN rm /chrome.deb
RUN apt-get update && apt-get install -y xvfb
COPY . /nessus-driver
WORKDIR /nessus-driver
RUN pip install -r requirements.txt
RUN chmod a+x nessus-entrypoint.sh