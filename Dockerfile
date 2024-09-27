# Use the official Python 3.11.10-bullseye image as a base
FROM python:3.11.10-bullseye

# Set environment variables
ENV POETRY_VERSION=1.8.2 
ENV HOME=/home/hacktor

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create a new user named 'hacktor'
RUN useradd -m hacktor

RUN mkdir -p /home/hacktor/app
RUN chown -R hacktor:hacktor /home/hacktor

# Switch to the 'hacktor' user
USER hacktor

# Set the working directory
WORKDIR $HOME/app

# Copy the current directory contents into the user's home directory
COPY .  $HOME/app/

# Install dependencies using Poetry
RUN poetry install

# Set the default entry point to use bash
ENTRYPOINT ["poetry", "run", "hacktor"]
