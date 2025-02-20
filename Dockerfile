FROM python:3.8

ENV HOME /Users/brody/IdeaProjects/CSE312-WebApp
WORKDIR /Users/brody/IdeaProjects/CSE312-WebApp

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u server.py