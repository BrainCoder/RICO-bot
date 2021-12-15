FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python3 -m pip install -U discord.py --noinput
RUN pip install SQLAlchemy --noinput
RUN pip install PyMySQL --noinput
RUN pip install better-profanity --noinput
RUN pip install tabulate --noinput
RUN python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus --noinput
RUN pip install python-gitlab --noinput

COPY . .

CMD [ "python", "./main.py" ]
