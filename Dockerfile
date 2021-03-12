FROM python:3.6

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -c "import nltk; nltk.download('framenet_v17')"

COPY src/ .

ENTRYPOINT ["python", "./mainpanel.py"]