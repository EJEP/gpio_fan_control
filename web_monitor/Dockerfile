FROM python:3.8.5-buster

WORKDIR fan_monitor

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "2", "--timeout", "90", "web_monitor:create_app()"]
