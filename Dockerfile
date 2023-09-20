FROM python:3.9.10-slim

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

WORKDIR /mcc_bot

COPY . /mcc_bot

CMD ["python", "scripts/note_bot.py"]