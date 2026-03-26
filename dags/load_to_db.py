import pandas as pd
from sqlalchemy import create_engine
import sys

def run_ingestion():
    # URL de connexion à la DB Postgres dans Docker
    # Note : On utilise 'db' comme hôte car le script tourne DANS le réseau Docker
    DATABASE_URL = "postgresql://user_data:password_data@db:5432/jobs_db"
    
    try:
        engine = create_engine(DATABASE_URL)
        df = pd.read_csv("jobs_with_technos.csv")
        
        print(f"🚀 Ingestion de {len(df)} lignes...")
        df.to_sql('stg_jobs', engine, if_exists='replace', index=False)
        print("✅ Données injectées avec succès dans PostgreSQL !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ingestion : {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_ingestion()