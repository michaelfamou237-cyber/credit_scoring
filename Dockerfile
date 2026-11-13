# 1. Utiliser l'image Python slim
FROM python:3.10-slim

# 2. Installer les bibliothèques système manquantes (dont libgomp1 pour LightGBM)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Définir le répertoire de travail
WORKDIR /app

# 4. Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le reste du code
COPY . .

# 6. Exposer le port (Render utilise le port 10000 par défaut)
EXPOSE 10000

# 7. Lancer l'application sur le port 10000
CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "10000"]
