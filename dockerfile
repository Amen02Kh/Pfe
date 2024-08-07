FROM kalilinux/kali-rolling:latest
WORKDIR /app
COPY . .
RUN apt update
RUN apt install python3-pip -y
RUN pip install -r requirements.txt
RUN apt-get install -y python3-apt
RUN apt-get install iputils-ping -y
RUN apt install wkhtmltopdf -y
RUN apt-get install -y dnsutils
RUN apt install smtp-user-enum -y
RUN apt install hydra -y
RUN apt install nmap -y
RUN  apt -y install exploitdb
CMD [ "python3","-m","flask","run","--host=0.0.0.0" ]