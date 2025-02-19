FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/leshack/DemandForecast.git .

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]