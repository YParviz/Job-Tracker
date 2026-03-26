from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random

def scrape_apec_angular(max_pages=20):
    # Notre dictionnaire de compétences à tracker
    TECHNOS_LIST = ["Python", "SQL", "Spark", "AWS", "Azure", "GCP", "Docker", "Airflow", "dbt", "Snowflake", "Kafka", "Scala", "Java", "Kubernetes"]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        page = context.new_page()
        
        all_jobs = []

        for cp in range(max_pages):
            url = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=Data%20Engineer&page={cp}"
            print(f"📂 Pipeline : Page {cp + 1}...")
            
            try:
                # 1. Attente du chargement Angular
                page.goto(url, wait_until="networkidle")
                
                # Fermer les cookies si besoin
                if cp == 0:
                    try: page.click("#onetrust-accept-btn-handler", timeout=3000)
                    except: pass

                # 2. Attente cruciale : on attend que la balise Angular <apec-offres> contienne des cartes
                page.wait_for_selector(".card-offer", timeout=20000)
                time.sleep(2)

                # 3. Récupération des liens des offres
                links = page.locator("a[href*='/detail-offre/']").all()
                # On utilise un set pour éviter les doublons (souvent 2 liens par carte sur l'APEC)
                hrefs = list(set([l.get_attribute("href") for l in links]))

                print(f"🔍 {len(hrefs)} liens identifiés. Analyse profonde en cours...")

                # 4. Crawl des offres une par une
                for href in hrefs:
                    try:
                        full_url = "https://www.apec.fr" + href
                        page.goto(full_url, wait_until="domcontentloaded")
                        time.sleep(1.5) # Temps de "lecture" humain

                        # Extraction brute pour les technos
                        # On cible la balise <main> qui contient le descriptif sur l'APEC
                        content = page.locator("main").inner_text()
                        title = page.locator("h1").inner_text().strip()
                        
                        found = [t for t in TECHNOS_LIST if t.lower() in content.lower()]
                        
                        all_jobs.append({
                            "title": title,
                            "technos": ", ".join(found),
                            "url": full_url
                        })
                        
                        # On repart sur la liste
                        page.go_back(wait_until="domcontentloaded")
                    except:
                        continue

            except Exception as e:
                print(f"⚠️ Erreur ou fin de liste à la page {cp + 1}")
                break
        
        browser.close()
        return all_jobs

if __name__ == "__main__":
    data = scrape_apec_angular(max_pages=20)
    if data:
        df = pd.DataFrame(data)
        df.to_csv("jobs_with_technos.csv", index=False, encoding='utf-8')
        print(f"✅ Pipeline terminé : {len(df)} jobs analysés.")