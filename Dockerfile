# Dockerfile
# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN groupadd -r app && useradd -r -g app app

# Create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy project
COPY . $APP_HOME

# Copy entrypoint script
COPY ./docker-entrypoint.sh $APP_HOME
RUN chmod +x $APP_HOME/docker-entrypoint.sh

# Copy wait-for script
COPY ./wait-for-it.sh $APP_HOME
RUN chmod +x $APP_HOME/wait-for-it.sh

# Chown all the files to the app user
RUN chown -R app:app $APP_HOME

# Change to the app user
USER app

# Run entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
