# Folosim o versiune oficială Python subțire
FROM python:3.11

# Setăm directorul de lucru în container
WORKDIR /backend

# Prevenim Python din a scrie fișiere .pyc pe disc și forțăm output-ul direct în terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalăm dependențele de sistem necesare (ex: pentru compilarea pachetelor de PostgreSQL precum psycopg2)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiem doar requirements.txt prima dată pentru a beneficia de layer caching-ul Docker
# Dacă schimbăm codul, dar nu adăugăm pachete noi, Docker nu va reinstala totul
COPY ./requirements.txt /backend/requirements.txt

# Instalăm dependențele Python
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

# Acum copiem întregul cod sursă (folderul app)
COPY ./app /backend/app

# Expunem portul 8000 pe care rulează Uvicorn (FastAPI)
EXPOSE 8000

# Comanda de pornire a serverului web
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]