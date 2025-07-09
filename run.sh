#!/bin/bash
# Script pour lancer l'application
if command -v docker-compose &> /dev/null; then
    echo "Lancement de MetalloBox..."
    docker-compose up --build
else
    echo "Docker Compose non trouvé. Installation de Python..."
    pip install -r requirements.txt
    python src/main.py
fi
