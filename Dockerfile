FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure backend directory is writable for SQLite (ctf.db)
RUN chmod -R 777 /app/backend

EXPOSE 7860

CMD ["gunicorn", "--chdir", "backend", "server:app", "--bind", "0.0.0.0:7860", "--workers", "2"]
