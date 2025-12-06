FROM python:3.11-slim
WORKDIR /app

# Install Flask and its dependencies.  Using `--no-cache-dir` keeps the
# image small.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app into the image (victim_app.py, templates/, static/, etc.)
COPY . .

# Expose the port the application listens on.  Docker Compose will
# map this to a host port.
EXPOSE 5000

# Environment variables for Flask.  FLASK_APP points to the
# application module.  FLASK_RUN_HOST and FLASK_RUN_PORT instruct
# `flask run` to bind to the correct host/port.
ENV FLASK_APP=victim_app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Default command: run the Flask development server.
CMD ["flask", "run"]
