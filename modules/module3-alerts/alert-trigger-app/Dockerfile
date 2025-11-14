FROM python:3.11-slim

WORKDIR /app

COPY app.py /app/app.py
RUN chmod +x /app/app.py

EXPOSE 8080

CMD ["python3", "/app/app.py"]

