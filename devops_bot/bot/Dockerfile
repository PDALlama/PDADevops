FROM ubuntu:20.04

RUN apt update && apt install python3 python3-pip -y
RUN pip3 install paramiko 
RUN pip3 install python-dotenv
RUN pip3 install pytelegrambotapi
RUN pip3 install psycopg2-binary
RUN apt install openssh-client -y

COPY bot.py /home/bot/
COPY .env /home/bot/

CMD ["python3","/home/bot/bot.py"]