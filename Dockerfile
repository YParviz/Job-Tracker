# Étape 1 : On part sur Debian pour avoir Python et Playwright sans erreur
FROM python:3.11-slim

# Étape 2 : Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Étape 3 : Installation de Dagu (on le récupère depuis son image officielle)
COPY --from=coralhl/dagu:latest /usr/local/bin/dagu /usr/local/bin/dagu

# Étape 4 : Installation des librairies Python (ça va marcher du 1er coup ici !)
RUN pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    playwright

# Étape 5 : Installation de Chromium pour le scraping
RUN playwright install --with-deps chromium

# Étape 6 : Configuration de l'environnement
WORKDIR /home/dagu/dagu
ENV DAGU_HOME=/home/dagu/dagu
EXPOSE 8080

# On lance le serveur Dagu
ENTRYPOINT ["dagu", "server", "--host", "0.0.0.0", "--port", "8080"]