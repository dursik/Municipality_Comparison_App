import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt

# 1. NASTAVENÍ STRÁNKY
st.set_page_config(page_title="Finanční Monitor Obcí", layout="wide")

# --- OCHRANA HESLEM ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("Přihlášení do aplikace")
    pwd = st.text_input("Zadejte heslo:", type="password")
    if st.button("Potvrdit"):
        if pwd == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Nesprávné heslo.")
    st.stop()

# 2. NAČTENÍ DAT (S CACHE PRO MAXIMÁLNÍ RYCHLOST)
@st.cache_data
def load_data():
    with open("points.pkl", "rb") as f:
        return pickle.load(f)

try:
    points = load_data()
except FileNotFoundError:
    st.error("Soubor points.pkl nebyl nalezen. Ujisti se, že je ve stejné složce jako tento skript.")
    st.stop()

# 3. LEVÝ PANEL - OVLÁDÁNÍ
st.sidebar.title("Finanční Monitor")
query = st.sidebar.text_input("Název obce nebo IČO:")

# Dynamický výběr roku ze souboru
dostupne_roky = sorted(points['Year'].dropna().unique().tolist(), reverse=True)
dostupne_roky_str = [str(int(rok)) for rok in dostupne_roky]
vybrany_rok_str = st.sidebar.selectbox("Rok analýzy:", dostupne_roky_str)

st.sidebar.markdown("---")
st.sidebar.subheader("Nastavení grafů")
bins_val = st.sidebar.number_input("Počet Bins:", min_value=10, max_value=100, value=40)

# Umožníme nechat osu X prázdnou pro automatické přizpůsobení
x_min = st.sidebar.number_input("Osa X od:", value=None, placeholder="Automaticky")
x_max = st.sidebar.number_input("Osa X do:", value=None, placeholder="Automaticky")

analyze_btn = st.sidebar.button("Analyzovat", type="primary", use_container_width=True)

# 4. POMOCNÁ FUNKCE PRO VÝPOČET MEZÍ GRAFU
def get_auto_bounds(data, mun_val, user_xmin, user_xmax):
    if data.empty:
        return user_xmin, user_xmax
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    auto_xmin = Q1 - 1.5 * IQR
    auto_xmax = Q3 + 1.5 * IQR
    
    if pd.notna(mun_val):
        if mun_val < auto_xmin: auto_xmin = float(mun_val)
        if mun_val > auto_xmax: auto_xmax = float(mun_val)
            
    final_xmin = user_xmin if user_xmin is not None else auto_xmin
    final_xmax = user_xmax if user_xmax is not None else auto_xmax
    return final_xmin, final_xmax

# 5. HLAVNÍ ČÁST APLIKACE A LOGIKA
st.title("Finanční Monitor Obcí")

# Spustíme analýzu, pokud uživatel klikl na tlačítko, nebo už má něco vyhledáno
if analyze_btn or query:
    if not query.strip():
        st.warning("Prosím zadej IČO nebo název obce v levém panelu.")
    else:
        query = query.strip()
        
        # Filtrování obce
        if query.isdigit():
            municipality_data = points[points['ICO'] == int(query)]
        else:
            if 'Name' in points.columns:
                municipality_data = points[points['Name'].str.contains(query, case=False, na=False)]
            else:
                st.error("Sloupec Name chybí.")
                st.stop()

        if municipality_data.empty:
            st.info("Zadaná obec nebo IČO nebylo nalezeno.")
        else:
            vybrany_rok = int(vybrany_rok_str)
            mun_year_data_df = municipality_data[municipality_data['Year'] == vybrany_rok]
            
            if mun_year_data_df.empty:
                st.warning(f"Pro zadanou obec nejsou v roce {vybrany_rok} dostupná žádná data.")
            else:
                mun_year_data = mun_year_data_df.iloc[0]
                category = mun_year_data['Category']
                category_data = points[(points['Category'] == category) & (points['Year'] == vybrany_rok)]

                # Vytvoření záložek
                tab1, tab2, tab3 = st.tabs(["Data Tabulka", "12 Ukazatelů", "Finální Skóre"])

                # --- ZÁLOŽKA 1: TABULKA ---
                with tab1:
                    st.subheader("Základní informace")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("IČO", mun_year_data['ICO'])
                    if 'Name' in mun_year_data:
                        col2.metric("Název obce", mun_year_data['Name'])
                    col3.metric("Rok analýzy", vybrany_rok)
                    col4.metric("Velikostní kategorie", category)

                    st.markdown("---")
                    st.subheader("Finanční Ukazatele")
                    
                    ratios = points.columns[5:17]
                    table_data = []
                    for ratio in ratios:
                        val = round(mun_year_data[ratio], 2) if pd.notna(mun_year_data[ratio]) else "N/A"
                        score_col = f"{ratio}_score"
                        score_val = mun_year_data.get(score_col, "N/A")
                        table_data.append({"Atribut nebo Ukazatel": ratio.replace("_", " "), "Hodnota": val, "Získané body": score_val})
                    
                    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

                    final_score = mun_year_data.get("Finální_skóre", "N/A")
                    st.success(f"### CELKOVÉ FINÁLNÍ SKÓRE: {final_score}")

                # --- ZÁLOŽKA 2: 12 GRAFŮ ---
                with tab2:
                    st.subheader("Distribuce v rámci kategorie")
                    fig, axes = plt.subplots(4, 3, figsize=(12, 10))
                    fig.patch.set_facecolor('white')
                    plt.subplots_adjust(hspace=0.5, wspace=0.3)
                    axes = axes.flatten()

                    for i, ratio in enumerate(ratios):
                        ax = axes[i]
                        data = category_data[ratio].dropna()
                        mun_val = mun_year_data.get(ratio, None)
                        
                        final_xmin, final_xmax = get_auto_bounds(data, mun_val, x_min, x_max)
                        
                        if final_xmin is not None and final_xmax is not None:
                            hist_data = data[(data >= final_xmin) & (data <= final_xmax)]
                            if hist_data.empty: hist_data = data
                        else:
                            hist_data = data

                        ax.hist(hist_data, bins=bins_val, color='#245375', edgecolor='white')
                        ax.set_title(ratio.replace("_"," "), fontsize=9)
                        
                        if pd.notna(mun_val):
                            ax.axvline(mun_val, color='#FF6130', linestyle='--', linewidth=3)

                        if final_xmin is not None and final_xmax is not None:
                            padding = (final_xmax - final_xmin) * 0.05
                            if padding == 0: padding = 1
                            ax.set_xlim(left=final_xmin - padding, right=final_xmax + padding)

                    st.pyplot(fig)

                # --- ZÁLOŽKA 3: FINÁLNÍ SKÓRE GRAF ---
                with tab3:
                    st.subheader("Distribuce finálního skóre")
                    fig_final, ax_final = plt.subplots(figsize=(8, 6))
                    fig_final.patch.set_facecolor('white')

                    final_col = "Finální_skóre"
                    data_final = category_data[final_col].dropna()
                    mun_val_final = mun_year_data.get(final_col, None)
                    
                    final_xmin, final_xmax = get_auto_bounds(data_final, mun_val_final, x_min, x_max)

                    if final_xmin is not None and final_xmax is not None:
                        hist_data_final = data_final[(data_final >= final_xmin) & (data_final <= final_xmax)]
                        if hist_data_final.empty: hist_data_final = data_final
                    else:
                        hist_data_final = data_final

                    ax_final.hist(hist_data_final, bins=bins_val, color='#245375', edgecolor='white')
                    ax_final.set_title("Finální Skóre", fontsize=14)
                    
                    if pd.notna(mun_val_final):
                        ax_final.axvline(mun_val_final, color='#FF6130', linestyle='--', linewidth=5)

                    if final_xmin is not None and final_xmax is not None:
                        padding = (final_xmax - final_xmin) * 0.05
                        if padding == 0: padding = 1
                        ax_final.set_xlim(left=final_xmin - padding, right=final_xmax + padding)

                    st.pyplot(fig_final)