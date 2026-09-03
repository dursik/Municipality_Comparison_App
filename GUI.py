import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import pickle 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

def get_resource_path(relative_path):
    """Získá absolutní cestu k souboru, funguje pro vývoj i pro PyInstaller .exe"""
    try:
        # PyInstaller vytváří dočasnou složku a ukládá cestu do sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Pokud kód pouštíme normálně přes Python, použije se aktuální složka
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class FinMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Finanční Monitor Obcí")
        self.root.geometry("1400x800")
        self.root.configure(bg="white")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TNotebook", background="white")
        style.configure("TNotebook.Tab", background="#f0f0f0", padding=[10, 5], font=("Arial", 10))
        
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e0e0e0")

        try:
            cesta_k_datum = get_resource_path("points_2025.pkl")
            with open(cesta_k_datum, "rb") as f:
                self.points: pd.DataFrame = pickle.load(f)
        except FileNotFoundError:
            messagebox.showerror("Chyba", "Soubor points_2025.pkl nebyl nalezen.")
            self.root.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        self.sidebar = ttk.Frame(self.root, width=250, relief="solid", borderwidth=1)
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)
        self.sidebar.pack_propagate(False)

        self.main_area = ttk.Frame(self.root)
        self.main_area.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        ttk.Label(self.sidebar, text="Finanční Monitor", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        
        ttk.Label(self.sidebar, text="Název obce nebo IČO:").pack(anchor="w", padx=10, pady=(10, 2))
        self.search_entry = ttk.Entry(self.sidebar)
        self.search_entry.pack(fill="x", padx=10, pady=2)
        
        # --- NOVÉ: Výběr roku ---
        ttk.Label(self.sidebar, text="Rok analýzy:").pack(anchor="w", padx=10, pady=(10, 2))
        
        # Získáme všechny unikátní roky z dat a seřadíme je sestupně (od nejnovějšího)
        dostupne_roky = sorted(self.points['Year'].dropna().unique().tolist(), reverse=True)
        # Převedeme roky na text pro zobrazení v Comboboxu
        dostupne_roky_str = [str(int(rok)) for rok in dostupne_roky]
        
        self.year_combobox = ttk.Combobox(self.sidebar, values=dostupne_roky_str, state="readonly")
        if dostupne_roky_str:
            self.year_combobox.current(0) # Automaticky vybere první (nejnovější) rok v seznamu
        self.year_combobox.pack(fill="x", padx=10, pady=2)
        # ------------------------

        ttk.Label(self.sidebar, text="Počet Bins (sloupců):").pack(anchor="w", padx=10, pady=(20, 2))
        self.bins_entry = ttk.Entry(self.sidebar)
        self.bins_entry.insert(0, "40")
        self.bins_entry.pack(fill="x", padx=10, pady=2)

        ttk.Label(self.sidebar, text="Osa X od (prázdné pro auto):").pack(anchor="w", padx=10, pady=(10, 2))
        self.x_min_entry = ttk.Entry(self.sidebar)
        self.x_min_entry.pack(fill="x", padx=10, pady=2)

        ttk.Label(self.sidebar, text="Osa X do (prázdné pro auto):").pack(anchor="w", padx=10, pady=(10, 2))
        self.x_max_entry = ttk.Entry(self.sidebar)
        self.x_max_entry.pack(fill="x", padx=10, pady=2)

        ttk.Button(self.sidebar, text="Analyzovat", command=self.analyze).pack(fill="x", padx=10, pady=30)

        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.pack(fill="both", expand=True)

        self.tab_table = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_table, text="Data Tabulka")
        
        self.tree = ttk.Treeview(self.tab_table, columns=("Metrika", "Hodnota", "Skore"), show="headings")
        self.tree.heading("Metrika", text="Atribut / Ukazatel")
        self.tree.heading("Hodnota", text="Hodnota")
        self.tree.heading("Skore", text="Získané body")
        
        self.tree.column("Metrika", width=350, anchor="w")
        self.tree.column("Hodnota", width=150, anchor="center")
        self.tree.column("Skore", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tree.tag_configure('header', font=("Arial", 10, "bold"), background="#d9edf7")
        self.tree.tag_configure('oddrow', background="#f9f9f9")
        self.tree.tag_configure('evenrow', background="#ffffff")
        self.tree.tag_configure('final', font=("Arial", 11, "bold"), background="#dff0d8")

        self.tab_dist = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dist, text="12 Ukazatelů")
        
        self.tab_final = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_final, text="Finální Skóre")

        self.canvas_dist = None
        self.canvas_final = None

    def analyze(self):
        query = self.search_entry.get().strip()
        if not query:
            return messagebox.showwarning("Upozornění", "Prosím zadej IČO nebo název obce.")

        if query.isdigit():
            municipality_data = self.points[self.points['ICO'] == int(query)]
        else:
            if 'Name' in self.points.columns:
                municipality_data = self.points[self.points['Name'].str.contains(query, case=False, na=False)]
            else:
                return messagebox.showerror("Chyba", "Sloupec 'Name' chybí.")

        if municipality_data.empty:
            return messagebox.showinfo("Výsledek", "Zadaná obec nebo IČO nebylo nalezeno.")

        # --- NOVÉ: Použití vybraného roku místo max() ---
        try:
            vybrany_rok = int(self.year_combobox.get())
        except ValueError:
            return messagebox.showerror("Chyba", "Prosím vyberte platný rok.")

        # Vyfiltrujeme data obce pouze pro konkrétní vybraný rok
        mun_year_data_df = municipality_data[municipality_data['Year'] == vybrany_rok]
        
        if mun_year_data_df.empty:
            return messagebox.showinfo("Upozornění", f"Pro zadanou obec nejsou v roce {vybrany_rok} dostupná žádná data.")
            
        mun_year_data = mun_year_data_df.iloc[0]
        category = mun_year_data['Category']

        # Získáme referenční data kategorie rovněž pro vybraný rok
        category_data = self.points[(self.points['Category'] == category) & (self.points['Year'] == vybrany_rok)]
        # ------------------------------------------------

        try:
            bins_val = int(self.bins_entry.get())
        except ValueError:
            bins_val = 40
            
        try:
            x_min = float(self.x_min_entry.get()) if self.x_min_entry.get() else None
        except ValueError:
            x_min = None
            
        try:
            x_max = float(self.x_max_entry.get()) if self.x_max_entry.get() else None
        except ValueError:
            x_max = None

        self.tree.delete(*self.tree.get_children()) 
        
        self.tree.insert("", "end", values=("ZÁKLADNÍ INFORMACE", "", ""), tags=('header',))
        self.tree.insert("", "end", values=("IČO", mun_year_data['ICO'], ""), tags=('oddrow',))
        if 'Name' in mun_year_data:
            self.tree.insert("", "end", values=("Název obce", mun_year_data['Name'], ""), tags=('evenrow',))
        # Aktualizováno na vybrany_rok
        self.tree.insert("", "end", values=("Rok analýzy", vybrany_rok, ""), tags=('oddrow',))
        self.tree.insert("", "end", values=("Velikostní kategorie", category, ""), tags=('evenrow',))
        
        self.tree.insert("", "end", values=("", "", "")) 
        self.tree.insert("", "end", values=("FINANČNÍ UKAZATELE", "Hodnota", "Body"), tags=('header',))

        ratios = self.points.columns[5:17]
        for idx, ratio in enumerate(ratios):
            val = round(mun_year_data[ratio], 2) if pd.notna(mun_year_data[ratio]) else "N/A"
            score_col = f"{ratio}_score"
            score_val = mun_year_data.get(score_col, "N/A")
            
            tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
            self.tree.insert("", "end", values=(ratio, val, score_val), tags=(tag,))

        self.tree.insert("", "end", values=("", "", "")) 
        final_score = mun_year_data.get("Finální_skóre", "N/A")
        self.tree.insert("", "end", values=("CELKOVÉ FINÁLNÍ SKÓRE", "", final_score), tags=('final',))

        self.draw_12_distributions(category_data, ratios, mun_year_data, bins_val, x_min, x_max)
        self.draw_final_distribution(category_data, "Finální_skóre", mun_year_data, bins_val, x_min, x_max)

        self.notebook.select(self.tab_table)

    def get_auto_bounds(self, data: pd.Series, mun_val, user_xmin, user_xmax):
        if data.empty:
            return user_xmin, user_xmax
            
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        auto_xmin = Q1 - 1.5 * IQR
        auto_xmax = Q3 + 1.5 * IQR
        
        if pd.notna(mun_val):
            if mun_val < auto_xmin:
                auto_xmin = float(mun_val)
            if mun_val > auto_xmax:
                auto_xmax = float(mun_val)
                
        final_xmin = user_xmin if user_xmin is not None else auto_xmin
        final_xmax = user_xmax if user_xmax is not None else auto_xmax
        
        return final_xmin, final_xmax

    def draw_12_distributions(self, cat_data, ratios, mun_data, bins_val, x_min, x_max):
        if self.canvas_dist:
            self.canvas_dist.get_tk_widget().destroy()

        fig, axes = plt.subplots(4, 3, figsize=(12, 10))
        fig.patch.set_facecolor('white')
        plt.subplots_adjust(hspace=0.5, wspace=0.3)
        axes = axes.flatten()

        for i, ratio in enumerate(ratios):
            ax = axes[i]
            data = cat_data[ratio].dropna()
            mun_val = mun_data.get(ratio, None)
            
            final_xmin, final_xmax = self.get_auto_bounds(data, mun_val, x_min, x_max)
            
            if final_xmin is not None and final_xmax is not None:
                hist_data = data[(data >= final_xmin) & (data <= final_xmax)]
                if hist_data.empty: 
                    hist_data = data
            else:
                hist_data = data

            ax.hist(hist_data, bins=bins_val, color='#245375', edgecolor='white')
            ax.set_title(ratio.replace("_"," "), fontsize=9)
            
            if pd.notna(mun_val):
                ax.axvline(mun_val, color='#FF6130', linestyle='--', linewidth=3)

            if final_xmin is not None and final_xmax is not None:
                padding = (final_xmax - final_xmin) * 0.05
                if padding == 0: 
                    padding = 1
                ax.set_xlim(left=final_xmin - padding, right=final_xmax + padding)

        self.canvas_dist = FigureCanvasTkAgg(fig, master=self.tab_dist)
        self.canvas_dist.draw()
        self.canvas_dist.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def draw_final_distribution(self, cat_data, final, mun_data, bins_val, x_min, x_max):
        if self.canvas_final:
            self.canvas_final.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('white')

        data = cat_data[final].dropna()
        mun_val = mun_data.get(final, None)
        
        final_xmin, final_xmax = self.get_auto_bounds(data, mun_val, x_min, x_max)

        if final_xmin is not None and final_xmax is not None:
            hist_data = data[(data >= final_xmin) & (data <= final_xmax)]
            if hist_data.empty: 
                hist_data = data
        else:
            hist_data = data

        ax.hist(hist_data, bins=bins_val, color='#245375', edgecolor='white')
        ax.set_title("Finální Skóre", fontsize=14)
        
        if pd.notna(mun_val):
            ax.axvline(mun_val, color='#FF6130', linestyle='--', linewidth=5)

        if final_xmin is not None and final_xmax is not None:
            padding = (final_xmax - final_xmin) * 0.05
            if padding == 0: 
                padding = 1
            ax.set_xlim(left=final_xmin - padding, right=final_xmax + padding)

        self.canvas_final = FigureCanvasTkAgg(fig, master=self.tab_final)
        self.canvas_final.draw()
        self.canvas_final.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinMonitorGUI(root)
    root.mainloop()