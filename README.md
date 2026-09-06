# Monitor finančního zdraví obcí

Tento projekt je analytický a vizualizační nástroj pro posouzení finančního zdraví obcí v České republice. Zpracovává účetní data obcí a převádí je na srozumitelné finanční ukazatele a vizualizace.

## Co aplikace dělá
Aplikace načte surová data z finančních výkazů obcí (výkaz plnění rozpočtu a rozvaha), vyčistí je a spočítá 12 klíčových finančních ukazatelů (např. finanční nezávislost, běžná likvidita, dluhová zátěž). Výsledky konkrétní obce pak porovná s rozdělením ostatních obcí ve stejné velikostní kategorii a spočítá celkové skóre finančního zdraví obce. Data si uživatel prohlíží v přehledném grafickém rozhraní (GUI).

## Zdroje dat
Všechna vstupní data pocházejí ze služby otevřených dat MONITOR Ministerstva financí ČR. Nic nevyžaduje registraci ani přihlášení.

| Data | URL | Použité soubory |
| --- | --- | --- |
| FIN 2-12 M (plnění rozpočtu) | `https://monitor.statnipokladna.gov.cz/data/extrakty/csv/FinM/<ROK>_12_Data_CSUIS_FINM.zip` | `FINM201_<ROK>012.csv` |
| Rozvaha | `https://monitor.statnipokladna.gov.cz/data/extrakty/csv/Rozvaha/<ROK>_12_Data_CSUIS_ROZV.zip` | `ROZV1_<ROK>012.csv`, `ROZV2_<ROK>012.csv` |
| Názvy obcí a počty obyvatel | ruční export z Analytické části `https://monitor.statnipokladna.gov.cz/analyza` | `FINM_PV.xlsx` |

Archivy s výkazem FIN a rozvahou mají zhruba 24 MB a po rozbalení zaberou přibližně 350 MB na rok. `FINM_PV.xlsx` se stahovat nedá, vzniká ručním exportem popsaným níže; pokrývá všechny roky najednou, takže stačí vytvořit ho jednou.

Každý archiv obsahuje víc souborů, než kolik jich zpracování potřebuje. Rozbalují se jen soubory uvedené v tabulce.

## Aktualizace dat
Data stáhne `download_script.py`, který uloží archivy, rozbalí z nich jen potřebné soubory a archivy zase smaže:

```
python download_script.py --year 2025 --data-dir data
```

Skript ve výchozím nastavení přeskakuje soubory, které už ve složce jsou, takže se dá spustit opakovaně; `--overwrite` je stáhne znovu.

Následně spusť tři skripty zpracování v tomto pořadí:

```
python data_cleaning_script.py --year 2025 --data-dir data
python ratios_script.py --year 2025
python distributions.py
```

Vznikne tak `data.pkl`, následně `ratios.pkl` a nakonec `percentiles.pkl` a `points.pkl`. GUI i aplikace ve Streamlitu čtou `points.pkl`.

`data_cleaning_script.py` ve výchozím nastavení zahrnuje šest předchozích let (`--years-back`), protože `ratios_script.py` potřebuje čtyřletý průměr příjmů pro vyhodnocení pravidla rozpočtové odpovědnosti. Ukazatele se počítají jen za poslední dva roky.

Názvy obcí a počty obyvatel se načítají z `FINM_PV.xlsx`, který se očekává ve složce s daty, pokud `--municipalities-file` neurčí jinou cestu. Obec se rozpoznává podle názvu ukončeného závorkou s okresem, což vylučuje součtové řádky za kraje a za celou ČR.

`FINM_PV.xlsx` je ruční export z Analytické části portálu MONITOR, sestava Finanční reporty > Územní organizace > Příjmy a výdaje. Do řádků patří dimenze `Rok (kód)`, `IČ (kód)`, `Obec (název)` a `Počet obyvatel (kód)`, ve filtru `Druh ÚJ (název)` hodnota Obce a v období celé roky (hodnoty bez uvedeného data, tedy stav k 31. 12.). Sestava se uloží přes Export do XLS. Řádky s popisem exportu nad hlavičkou skript přeskočí sám.

## Spuštění aplikace
Nejprve nainstaluj závislosti:

```
pip install -r requirements.txt
```

Obě rozhraní čtou `points.pkl` z kořenové složky projektu, takže je nutné mít nejdřív hotové zpracování dat popsané výše.

### Desktopové rozhraní
```
python GUI.py
```

Otevře se okno postavené na knihovně tkinter, která je součástí standardní instalace Pythonu. Pokud `points.pkl` chybí, aplikace to ohlásí a skončí.

### Webové rozhraní
```
python run_web_script.py
```

Aplikace poběží na `http://localhost:8501` a otevře se v prohlížeči. Skript před spuštěním ověří, že existuje `points.pkl`, upozorní na chybějící soubor s heslem a použije stejný interpret Pythonu, kterým byl sám spuštěn, takže ve virtuálním prostředí není potřeba nic aktivovat. Port změní `--port`, přepínač `--headless` neotevře prohlížeč.

Totéž jde spustit i přímo:

```
streamlit run app.py
```

Při úplně prvním spuštění se Streamlit nejdřív zeptá na e-mailovou adresu pro odběr novinek. Stačí potvrdit prázdný řádek klávesou Enter a aplikace naběhne; podruhé už se dotaz neobjeví. Pokud se aplikace spouští neinteraktivně, kde není možné na dotaz odpovědět, přeskočí ho přepínač `--headless`, respektive `--server.headless true` při přímém spuštění.

Aplikace je chráněná heslem, které se načítá ze souboru `.streamlit/secrets.toml`. Ten není součástí repozitáře (je uvedený v `.gitignore`), takže si ho vytvoř s vlastním heslem:

```
app_password = "zvolene-heslo"
```

Bez tohoto souboru se aplikace zastaví na přihlašovací obrazovce.

## Předpoklady
*Vstupní data ze systému Státní pokladny (výkazy FIN a ROZV) jsou ve standardizovaném formátu CSV.
*Pro spuštění zdrojového kódu musí mít uživatel nainstalovaný Python 3.10+ a knihovny uvedené v souboru requirements.txt.
*Pro běžné uživatele je v sekci Releases k dispozici zkompilovaná verze .exe, která nevyžaduje instalaci.

## Omezení
*Aplikace GUI nepracuje s živými síťovými daty. Načítá předpočítaný dataset (points.pkl). Pro aktualizaci dat je nutné stáhnout nové soubory CSV a znovu ručně spustit příslušné skripty.
*Porovnání probíhá vždy striktně v rámci jedné velikostní kategorie obcí (podle počtu obyvatel), aby bylo hodnocení spravedlivé.
*Malý počet obcí ve výsledcích chybí, protože podaly výkaz FIN, ale nikoli rozvahu, takže u nich nelze spočítat ukazatele likvidity. Jde o mezery ve zdrojových datech, nikoli o chybu zpracování.

## Možná vylepšení
* **Export reportu:** Možnost vygenerovat a stáhnout analýzu vybrané obce ve formátu PDF přímo z GUI.
* **Interaktivní grafy:** Přechod z Matplotlibu na knihovny typu Plotly pro dynamičtější vizualizaci dat (např. zobrazení hodnot po najetí myší).

---
Poznámka: Architektura grafického rozhraní (GUI) a tento soubor README byly vytvořeny s pomocí umělé inteligence (AI).
---