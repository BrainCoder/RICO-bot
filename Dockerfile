FROM python:3

WORKDIR /usr/src/app

RUN python3 -m pip install -U discord.py
RUN pip install SQLAlchemy
RUN pip install PyMySQL
RUN pip install better-profanity
RUN pip install tabulate
RUN python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus
RUN pip install python-gitlab

COPY . .

CMD [ "python", "./main.py" ]
