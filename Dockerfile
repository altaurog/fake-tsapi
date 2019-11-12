FROM python:3.7

COPY requirements.txt /install/
RUN pip install -r /install/requirements.txt

COPY api/ /opt/api/
WORKDIR /opt/
EXPOSE 8000
CMD ["uvicorn", "api.app:app"]
