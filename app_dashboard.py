import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. Connexion à la base de données
DATABASE_URL = "postgresql://user_data:password_data@localhost:5432/jobs_db"

def load_data():
    engine = create_engine(DATABASE_URL)
    query = "SELECT title, technos, url FROM stg_jobs"
    return pd.read_sql(query, engine)

st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")
st.title("📊 Analyse des technos Data Engineer")

df = load_data()

# 2. Traitement des technos (Explode pour le graphique)
df['technos_list'] = df['technos'].str.split(', ')
df_exploded = df.explode('technos_list')
df_exploded['technos_list'] = df_exploded['technos_list'].str.strip()

# 3. Sidebar : FILTRE UNIQUE
# On prépare la liste propre des technos pour le menu
all_techs = sorted([str(t) for t in df_exploded['technos_list'].dropna().unique()])

# On ne crée le multiselect qu'UNE SEULE FOIS
selected_tech = st.sidebar.multiselect(
    "Filtrer par technologie", 
    all_techs, 
    key="filtre_techno_unique"
)

# Application du filtre sur les données
if selected_tech:
    df_filtered = df[df['technos'].apply(lambda x: any(t in str(x) for t in selected_tech))]
else:
    df_filtered = df

# 4. Affichage du Top Technos (Graphique)
st.subheader("🚀 Top 10 des technologies les plus demandées")
tech_counts = df_exploded['technos_list'].value_counts().head(10)
st.bar_chart(tech_counts)

# 5. Table de données interactive
st.subheader(f"🔍 Liste des offres ({len(df_filtered)} résultats)")
st.dataframe(
    df_filtered[['title', 'technos', 'url']],
    column_config={
        "url": st.column_config.LinkColumn("Lien vers l'offre")
    },
    hide_index=True,
    use_container_width=True
)