FROM python:3.8.2

ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

RUN apt-get update \
    && apt-get install -y netcat

# Set the working directory to /app
ENV APP=/app
WORKDIR $APP

# Copy the requirements file into the container
COPY requirements.txt $APP

# Install the requirements
RUN pip3 install -r requirements.txt

# Copy the rest of the project files into the container
COPY . $APP

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangobackend.wsgi"]
