FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/spgdaman/recon_automator.git .

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7070", "--server.address=localhost"]