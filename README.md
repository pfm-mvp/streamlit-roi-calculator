# 📄 Streamlit ROI Calculator – Documentatie

**Laatste update:** 6 augustus 2025  
**Auteur:** ChatGPT t.b.v. [Gebruiker]

---

## 🎯 Doel van de App

Deze Streamlit-app simuleert de **impact van een conversieverbetering op zaterdagen** op de totale omzet van een retailportfolio, op basis van data uit de Vemcount API. De app dient als ROI-calculator en proof-of-concept voor hoe slimme inzichten gegenereerd kunnen worden uit bestaande klantentellers.

---

## 🔧 Technologieën

- **Streamlit** (frontend & interactieve interface)
- **FastAPI** (interne API-wrapper die communiceert met de Vemcount API)
- **Vemcount API** (data-bron voor bezoekersaantallen, conversie, omzet etc.)
- **Python** (dataverwerking, visualisatie en simulaties)

---

## 🗂️ Bestandsstructuur

\`\`\`bash
project/
├── app.py                        # Homepagina van Streamlit-app
├── zaterdag_calculator.py        # Conversieboost-simulatie per zaterdag
├── data_transformer.py           # Functie om Vemcount JSON-response te normaliseren
├── requirements.txt              # Dependencies voor deployment
└── .streamlit/
    └── secrets.toml              # Bevat API_URL (verwijzing naar FastAPI endpoint)
\`\`\`

---

## 🧠 Functionele werking

1. **Vraagt data op** bij Vemcount via een FastAPI-wrapper.
2. Filtert enkel **zaterdagen** uit de dataset.
3. Simuleert extra omzet op basis van een opgegeven **conversieboost (%)**.
4. Berekent:
   - Extra klanten
   - Extra omzet
   - Nieuwe totale omzet
   - Groei in %
5. Toont resultaten als **tabel + staafgrafiek** per winkel.

---

## 📤 Vemcount API-aanroep (via FastAPI)

De functie `get_kpi_data_for_stores()` stuurt de volgende query naar de interne FastAPI:

```python
params = [
    ("data", shop_id),
    ("data_output", "count_in"),
    ("data_output", "conversion_rate"),
    ("data_output", "turnover"),
    ("data_output", "sales_per_transaction"),
    ("source", "shops"),
    ("period", "last_year"),
    ("step", "day")
]
```

De server vertaalt dit naar een correcte `POST`-aanroep naar de Vemcount `/report` endpoint en retourneert JSON met dagelijkse KPI’s per shop.

---

## 🔄 Normalisatie van data

In `data_transformer.py` zetten we de response om in een nette DataFrame:

| shop_id | date       | turnover | count_in | conversion_rate | sales_per_transaction |
|---------|------------|----------|----------|------------------|------------------------|
| 26304   | 2024-01-06 | 1023.00  | 100      | 0.25             | 40.92                  |

Alleen zaterdagen worden gefilterd en doorgerekend.

---

## ✅ Debug verwijderen

Tijdens ontwikkeling zat er uitgebreide debug-output in:

- `st.write()`
- `st.json()`
- `st.warning()` bij ontbrekende keys

Na oplevering zijn **alle `if debug:`-blokken** en overige `st.write()`-calls verwijderd om de app productieklaar te maken.

---

## 🚀 Deployment

De app is gedeployed via:

- **Streamlit Sharing** (public of private repo)
- `.streamlit/secrets.toml` bevat:

```toml
API_URL = "https://vemcount-agent.onrender.com/get-report"
```

Gebruik `streamlit run app.py` lokaal of deploy via [Streamlit Community Cloud](https://streamlit.io/cloud)

---

## 💡 Lessen (FastAPI + Vemcount integratie)

1. **De Vemcount API is krachtig, maar strikt**:
   - Arrays moeten als `?data=...&data=...` (niet `data[]`)
   - Auth via Bearer Token vereist

2. **Wrapper via FastAPI zorgt voor beheersbaarheid**:
   - We kunnen logging, validatie en foutafhandeling centraal afvangen
   - Frontend (Streamlit) hoeft geen auth of logica te bevatten

3. **Normalisatie is cruciaal**:
   - De response van Vemcount is nested per shop > per datum > per KPI
   - Deze moet worden ge-flattened voor analyse in Pandas

4. **Streamlit is ideaal voor iteratie en demo's**:
   - Snel bouwen, sliders gebruiken, resultaten tonen zonder frontend gedoe

---

## 📌 Volgende stappen (optioneel)

- 📈 ROI in maanden berekenen o.b.v. kosten & extra omzet
- 🧾 Toevoegen van KPI-kaarten
- 📥 CSV-export
- 🌍 Meertalige versie (NL/EN)
- 📊 Koppeling met Looker Studio of Power BI

---

**Voor overdracht aan een ontwikkelaar of uitbreiding van het project, raadpleeg dit document als basis.**
