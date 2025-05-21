FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir dj-database-url

# Copy project files
COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
# Run migrations\n\
python manage.py migrate\n\
# Create superuser\n\
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username=\"admsrv\").exists() or User.objects.create_superuser(\"admsrv\", \"admin@example.com\", \"adminpass\")"\n\
# Start server\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
