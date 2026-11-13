# 1. Utiliser une image Python légère officielle
FROM python:3.10-slim

# 2. Définir le répertoire de travail dans le conteneur
WORKDIR /app

# 3. Copier uniquement le fichier requirements.txt d'abord (pour optimiser le cache Docker)
COPY requirements.txt .

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le reste de votre projet (App.py, models/, static/, etc.)
COPY . .

# 6. Exposer le port 8000 (le port par défaut d'Uvicorn/FastAPI)
EXPOSE 8000

# 7. Lancer l'application avec Uvicorn
# On utilise "App:app" car le fichier s'appelle App.py et l'instance FastAPI s'appelle app
CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "8000"]
