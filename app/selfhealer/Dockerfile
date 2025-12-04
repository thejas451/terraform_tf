FROM python:3.11-slim

WORKDIR /app

# Copy script
COPY selfhealer.py /app/selfhealer.py

# Install required Python packages
RUN pip install --no-cache-dir kubernetes requests

# Avoid Python buffering problems
ENV PYTHONUNBUFFERED=1

CMD ["python", "selfhealer.py"]
