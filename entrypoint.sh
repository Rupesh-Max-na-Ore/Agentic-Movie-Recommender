#!/bin/bash

echo "📥 Downloading model files..."

python download_model.py

echo "⏳ Waiting for PostgreSQL..."

# Wait until DB is ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "✅ Database is up!"

echo "📦 Initializing database..."

python data_processor.py



echo "🚀 Starting Streamlit app..."

streamlit run app.py --server.address=0.0.0.0