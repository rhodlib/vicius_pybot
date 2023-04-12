FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -U nextcord python-dotenv wavelinkcord

CMD python -u ./vicius_pybot.py