#!/bin/bash
echo "Building Emergency Minute app..."

# Upgrade pip
pip install -r requirements.txt

# Create database directory and initialize
python -c "
from app import create_app, db
import os
os.makedirs('/tmp', exist_ok=True)
app = create_app()
with app.app_context():
    db.create_all()
    print('SQLite database initialized!')
"

echo "Build completed!"