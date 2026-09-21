FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask

# Copy the application
COPY app.py /app/app.py

# Create a flag file
RUN echo "CTF{demo_sql_injection_flag_12345}" > /flag.txt

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
