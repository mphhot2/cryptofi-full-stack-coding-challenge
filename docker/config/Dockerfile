# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY /api/requirements.txt .
COPY /api/src ./src
COPY /docker ./docker
COPY /api/test ./test
COPY /api/data ./data


# Install pip requirements
RUN python -m pip install -r requirements.txt


ENV PYTHONPATH "${PYTHONPATH}:/src:/test"

CMD ["sh", "./docker/scripts/entrypoint.sh"]