# Use slim Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]