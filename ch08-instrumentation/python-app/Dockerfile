FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# site-packages を見て、入っているライブラリ（Flask 等）に対応する
# 計装ライブラリを自動導入する。
RUN opentelemetry-bootstrap -a install

COPY app.py .

# python app.py を opentelemetry-instrument で包む。コードは変えない。
CMD ["opentelemetry-instrument", "python", "app.py"]
