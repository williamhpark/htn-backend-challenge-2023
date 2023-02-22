FROM python:3.8

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN apt-get install -y python3-pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir /db

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
