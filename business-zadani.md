# Business zadání – Finanční monitor obcí

| Položka | Hodnota |
|---|---|
| Pracovní název | Finanční monitor obcí (FMO) |
| Repozitář | `csas-dev/corpai-municipality-comparison-discovery`; originál na soukromém účtu `MichalJenik/Municipality_Comparison_App` |
| Verze dokumentu | **2.0** |
| Stav řešení | **Produkčně používaný nástroj bez technického správce.** Tým přes něj zpracovává vyšší desítky klientských projektů ročně, výstupy slouží jako podklad pro obce a města. Předaný snímek je bez historie v gitu, bez testů a bez předané dokumentace metodiky |
| Byznys vlastník | Michal Jeník – Infrastrukturní poradenství, Corporate Finance |
| Autor kódu | Denis Šmerda – **odešel z ČS ke konkurenci** (Barclays); licence MIT vedena na soukromou osobu |
| Datum analýzy | 2026-08-06 |

---

## 1. Manažerské shrnutí

Převzatá aplikace je **nástroj pro rychlé posouzení finančního zdraví české obce**. Pro každou obec (celkem 6 247 obcí, roky 2024 a 2025) spočítá 12 finančních ukazatelů z veřejných dat Ministerstva financí ČR, porovná je s obcemi **stejné velikostní kategorie** a přiřadí souhrnné **Finální skóre v rozsahu 0–10 bodů**.

Uživatel zadá název obce nebo IČO, vybere rok a okamžitě vidí:
1. tabulku hodnot 12 ukazatelů a bodů za každý z nich,
2. celkové skóre obce,
3. histogramy rozdělení každého ukazatele v dané velikostní kategorii s vyznačenou pozicí zkoumané obce.

**Hlavní přínos:** nahrazuje ruční stahování a zpracování výkazů z portálu MONITOR (dnes práce na hodiny) odpovědí v řádu sekund a poskytuje poradci srozumitelné srovnání „jak si obec stojí vůči srovnatelným obcím“.

**Hlavní upozornění:** aplikace **už se produkčně používá** – tým Infrastrukturní poradenství přes ni zpracovává vyšší desítky klientských projektů ročně, výstupy dostávají obce a města jako podklad pro rozhodnutí o investicích a banka nástroj veřejně komunikovala v článku z 28. 5. 2026. Zároveň analýza odhalila, že **obec v provozním schodku dostává u ukazatele s nejvyšší vahou maximální počet bodů**, že vyhledávání bez varování zobrazí jinou obec stejného jména, že autentizace stojí na jednom sdíleném heslu a že datovou pipeline nelze bez zásahu do zdrojového kódu vůbec spustit – přitom její roční spuštění je hlavním požadavkem zadání.

Nejde tedy o rozhodnutí „nasadit / nenasadit“, ale o **stabilizaci a převzetí běžící, byznysově kritické a klientsky viditelné služby**. Detaily viz kap. 9, [docs/technicka-specifikace.md](docs/technicka-specifikace.md) a [docs/prevzeti-provoz-a-backlog.md](docs/prevzeti-provoz-a-backlog.md).

### 1.1 Skutečný stav využití

| Skutečnost | Doklad |
|---|---|
| „Klíčový nástroj naší práce“, vyšší desítky klientských projektů ročně | e-mail M. Jeníka, 10. 7. 2026 |
| Výstupy jdou externím klientům jako „komplexní analýza“ | článek ČS, 28. 5. 2026 |
| Banka nástroj veřejně komunikovala | článek ČS, 28. 5. 2026 |
| Zvažuje se zpřístupnění klientům / veřejnosti | diskuse pod článkem (dotaz zastupitele Olomouce) |
| Autor kódu odešel ke konkurenci, byznys si netroufá do kódu zasáhnout | e-maily 10. 7. a 29. 7. 2026 |
| Data jsou výhradně veřejná z MONITOR MF ČR, **žádná interní data ČS** | e-mail M. Jeníka, 27. 7. 2026 |

### 1.2 Co banka od převzetí očekává

| Požadavek | Frekvence |
|---|---|
| Aktualizace rozpočtových dat všech obcí dle MONITOR MF ČR | **1× ročně, okno březen–duben** (nejbližší: data k 12/2026) |
| Drobné úpravy metodiky | **cca 1× za půl roku** |
| Zoficiálnění aplikace a zajištění dlouhodobé správy | jednorázově |

---

## 2. Kontext a problém, který řešíme

Banka financuje obce a města (municipální a veřejný sektor). Pro obchodní i risk rozhodování je potřeba rychlá orientace v hospodaření konkrétní obce:

* Data existují – Ministerstvo financí ČR je publikuje (portál MONITOR: výkaz FIN 2-12 M, Rozvaha) – ale jsou v podobě rozsáhlých CSV exportů podle rozpočtové skladby, které nejsou přímo interpretovatelné.
* Absolutní čísla nejsou samy o sobě vypovídající: obec s 80 obyvateli a město se 40 tisíci obyvateli nelze porovnávat přímo.
* Dnešní praxe (bez nástroje) znamená ruční přípravu podkladů v Excelu, která je pracná, neopakovatelná a obtížně auditovatelná.

**Problém:** Neexistuje standardizovaný, opakovatelný a rychlý způsob, jak posoudit relativní finanční kondici obce vůči srovnatelné skupině.

**Současné řešení tento problém již řeší** – tým Infrastrukturní poradenství jej používá jako vstupní diagnostiku, na kterou navazuje hlubší práce bankeře s klientem, a jako přirozený vstup do navazujících služeb (financování, investiční strategie, finanční modelování). Zadání proto není „postavit nástroj“, ale **udržet a zkvalitnit již běžící službu**.

---

## 3. Cíl řešení

| # | Cíl | Měřitelný ukazatel úspěchu |
|---|---|---|
| C1 | Zkrátit přípravu finančního přehledu o obci | z hodin na < 1 minutu |
| C2 | Standardizovat metodiku posouzení | 100 % uživatelů pracuje se stejnou metodikou a stejnou datovou základnou |
| C3 | Umožnit srovnání s peer skupinou | každý ukazatel zobrazen v kontextu rozdělení obcí stejné velikosti |
| C4 | Poskytnout jednu souhrnnou metriku pro rychlý triage | Finální skóre 0–10 |
| C5 | Zajistit dohledatelnost a auditovatelnost | každé číslo musí být zpětně odvoditelné ze zdrojového výkazu a verze metodiky |

---

## 4. Cílová skupina a persony

| Persona | Role | Typické použití | Technická zdatnost |
|---|---|---|---|
| **Relationship manager / obchodník veřejného sektoru** | primární uživatel | příprava na jednání se starostou, rychlý přehled před schůzkou | nízká – potřebuje „zadat obec, kliknout, číst“ |
| **Úvěrový analytik / risk** | sekundární uživatel | vstupní screening před detailní analýzou, sanity check | střední |
| **Produktový / segmentový manažer** | příležitostný | pohled na portfolio a strukturu segmentu | nízká |
| **Metodik / model owner** | vlastník metodiky | schvaluje vah, prahy, výklad ukazatelů | vysoká doménová, nízká technická |
| **Datový inženýr / správce aplikace** | provoz | roční přepočet dat, provoz aplikace | vysoká |

Zadání explicitně počítá s tím, že **primární uživatelé nejsou techničtí** – z toho plynou požadavky na jednoduchost UI, srozumitelné popisky a jednoznačné chování vyhledávání.

---

## 5. Business use cases

| ID | Use case | Popis | Priorita |
|---|---|---|---|
| UC-01 | Vyhledání obce | Uživatel zadá název obce nebo IČO a systém jednoznačně identifikuje obec. Při více shodách nabídne výběr. | Must |
| UC-02 | Zobrazení karty obce | IČO, název, okres, rok, velikostní kategorie, počet obyvatel. | Must |
| UC-03 | Přehled ukazatelů | Tabulka 12 ukazatelů: hodnota, získané body, směr hodnocení, váha. | Must |
| UC-04 | Souhrnné skóre | Finální skóre 0–10 včetně slovní interpretace pásma. | Must |
| UC-05 | Srovnání s peer skupinou | Histogram rozdělení ukazatele ve velikostní kategorii s vyznačením pozice obce. | Must |
| UC-06 | Volba roku | Výběr roku analýzy z dostupných let. | Must |
| UC-07 | Meziroční srovnání | Zobrazení vývoje skóre a ukazatelů obce v čase. | Should (dnes chybí) |
| UC-08 | Export podkladu | Export karty obce do PDF/XLSX jako příloha do úvěrového spisu. | Should (dnes chybí) |
| UC-09 | Portfoliový pohled | Seznam obcí filtrovaný podle skóre / kategorie / kraje. | Could (dnes chybí) |
| UC-10 | Zobrazení metodiky | Uživatel si zobrazí definici ukazatele, vzorec a zdroj dat. | Must (dnes chybí) |

### 5.1 Explicitní změnové požadavky byznysu

Zadány v e-mailu M. Jeníka z 27. 7. 2026. Technický rozbor v [docs/prevzeti-provoz-a-backlog.md](docs/prevzeti-provoz-a-backlog.md), kap. 5.2.

| ID | Požadavek | Dopad na skóre | Priorita |
|---|---|---|---|
| CR-01 | Roční aktualizace dat dle MONITOR MF ČR (nejblíže k 12/2026), okno březen–duben | vše | **Nejvyšší** |
| CR-02 | Daň z nemovitých věcí přepočítat **na obyvatele** a zobrazovat v čitelných jednotkách; současné zobrazení v desítkách milionů Kč je pro klienty obtížně interpretovatelné | žádný – ukazatel má váhu 0 % | Vysoká |
| CR-03 | Položka **17a – Transfery z komerční činnosti** se má odčítat od položky **16 – Mimořádné dotace**, nikoli od položky **13 – Ostatní nedaňové příjmy** | **20 %** (Finanční nezávislost 5 % + Finanční soběstačnost 15 %) | Vysoká |

> **CR-02 nezávisle potvrzuje nález Z16** této analýzy (ukazatel je absolutní částka, nikoli poměr). Byznys naráží na stejný problém v praxi s klientem.
>
> **CR-03 vyžaduje před nasazením kvantifikaci dopadu** – mění pětinu finálního skóre a je nutné rozhodnout, zda se přepočítají již vydané klientské analýzy.
>
> **CR-01 nelze dnes splnit** – datová pipeline není spustitelná (Z8) a chybějí vstupní data z MONITORu.

---

## 6. Rozsah

### 6.1 V rozsahu (in scope)

* Obce České republiky (dle registru MONITOR), aktuálně 6 247 subjektů.
* Roky 2024 a 2025 (řešení je navrženo tak, že drží vždy **poslední dva** dostupné roky).
* 12 finančních ukazatelů definovaných v kap. 7.
* Bodové hodnocení a souhrnné skóre.
* Vizualizace rozdělení v rámci velikostní kategorie.
* Webová aplikace pro interní uživatele.

### 6.2 Mimo rozsah (out of scope)

* Kraje, dobrovolné svazky obcí, příspěvkové organizace, městské části.
* Nefinanční ukazatele (demografie, nezaměstnanost, majetková struktura, dotační potenciál).
* Napojení na core bankovní systémy, CRM nebo úvěrový proces.
* Automatické rozhodování o úvěru – nástroj je **výhradně podpůrný** (viz kap. 10).
* Externí/klientský přístup – nástroj je čistě interní.

---

## 7. Metodika – business popis

### 7.1 Princip

1. **Peer skupina.** Obce se rozdělí do 12 velikostních kategorií podle počtu obyvatel. Obec je vždy hodnocena pouze vůči obcím ve stejné kategorii a stejném roce.
2. **Body 0–10.** Pro každý ukazatel se určí 11 pásem. U šesti ukazatelů jsou pásma odvozena z reálného rozdělení dat v kategorii (decily, po vyloučení odlehlých hodnot). U dalších šesti jsou pásma **pevně stanovena metodikou** a jsou stejná pro všechny kategorie i roky.
3. **Směr hodnocení.** U ukazatelů typu „čím méně, tím lépe“ (zadlužení) je bodová škála obrácená.
4. **Finální skóre** = vážený součet bodů; váhy dávají v součtu 1,0; výsledek je opět v rozsahu 0–10.

### 7.2 Ukazatele a váhy

| # | Ukazatel | Jednotka | Směr | Váha | Typ pásem |
|---|---|---|---|---|---|
| 1 | Celkové příjmy na jednoho obyvatele | Kč/obyv. | vyšší = lépe | 5 % | z dat (decily) |
| 2 | Daňové příjmy na jednoho obyvatele | Kč/obyv. | vyšší = lépe | **0 %** | z dat (decily) |
| 3 | Finanční nezávislost | % | vyšší = lépe | 5 % | z dat (decily) |
| 4 | Finanční soběstačnost | % | vyšší = lépe | 15 % | z dat (decily) |
| 5 | Výše dluhu k saldu běžného rozpočtu | násobek | nižší = lépe | **20 %** | pevná |
| 6 | Krytí dluhu provozním přebytkem | násobek | nižší = lépe | 15 % | pevná |
| 7 | Krytí kapitálových výdajů investičními transfery | % | vyšší = lépe | 5 % | z dat (decily) |
| 8 | Pravidlo rozpočtové odpovědnosti | % | nižší = lépe | 15 % | pevná |
| 9 | Podíl cizích zdrojů na aktivech | % | nižší = lépe | 5 % | pevná |
| 10 | Běžná likvidita | násobek | vyšší = lépe | 10 % | pevná |
| 11 | Rychlá likvidita | násobek | vyšší = lépe | 5 % | pevná |
| 12 | Daň z nemovitosti | Kč (absolutně) | vyšší = lépe | **0 %** | z dat (decily) |
| | **Celkem** | | | **100 %** | |

> **Změnový požadavek CR-02** mění ukazatel č. 12 na hodnotu **na obyvatele**. Váha zůstává 0 % – nutno potvrdit, zda to tak má zůstat.
> **Změnový požadavek CR-03** mění společný čitatel ukazatelů č. 3 a č. 4, tedy **20 % finálního skóre**.

> **Pozor (business dopad):** ukazatele **č. 2 a č. 12 mají nulovou váhu** – uživateli se v tabulce zobrazují včetně bodů, ale na výsledné skóre nemají žádný vliv. Buď je nutné jim váhu přiřadit, nebo je v UI jasně označit jako pouze informativní.

### 7.3 Velikostní kategorie a jejich obsazenost (rok 2025)

| Kategorie (počet obyvatel) | Počet obcí | Statistická vypovídací hodnota peer srovnání |
|---|---|---|
| 0–100 | 391 | dobrá |
| 101–200 | 953 | dobrá |
| 201–500 | 1 998 | dobrá |
| 501–1 000 | 1 374 | dobrá |
| 1 001–2 000 | 802 | dobrá |
| 2 001–5 000 | 452 | dobrá |
| 5 001–10 000 | 145 | přijatelná |
| 10 001–20 000 | 68 | slabá |
| 20 001–50 000 | 46 | slabá |
| 50 001–100 000 | 12 | **nedostatečná** |
| 100 001–1 000 000 | 5 | **nedostatečná** |
| nad 1 000 000 | 1 (Praha) | **srovnání nedává smysl** |

> **Business dopad:** u velkých měst – tedy u klientů s největší expozicí – je percentilové srovnání statisticky bezcenné. Pro Prahu je „porovnání s peer skupinou“ porovnání sama se sebou.

---

## 8. Požadavky

### 8.1 Funkční požadavky

| ID | Požadavek | Priorita | Stav v převzatém řešení |
|---|---|---|---|
| FR-01 | Vyhledání obce podle názvu (bez ohledu na diakritiku a velikost písmen) | Must | částečně – citlivé na diakritiku, padá na závorkách |
| FR-02 | Vyhledání obce podle IČO ve standardním osmimístném tvaru včetně úvodních nul | Must | **nesplněno** – IČO uloženo číselně, úvodní nuly ztraceny |
| FR-03 | Při více shodách zobrazit seznam a nechat uživatele vybrat | Must | **nesplněno** – vybere se první shoda bez upozornění |
| FR-04 | Zobrazit identifikaci obce (IČO, název, okres, počet obyvatel, kategorie) | Must | splněno (kromě samostatného pole okres) |
| FR-05 | Zobrazit 12 ukazatelů s hodnotou a body | Must | splněno |
| FR-06 | Zobrazit Finální skóre | Must | splněno |
| FR-07 | Zobrazit histogram rozdělení pro každý ukazatel s pozicí obce | Must | splněno |
| FR-08 | Volba roku analýzy | Must | splněno |
| FR-09 | Zobrazit u každého ukazatele jeho definici, směr a váhu | Must | **nesplněno** |
| FR-10 | Zobrazit datum a verzi dat, ze kterých se počítá | Must | **nesplněno** |
| FR-11 | Meziroční vývoj obce | Should | nesplněno |
| FR-12 | Export do PDF/XLSX | Should | nesplněno |
| FR-13 | Uložení / sdílení odkazu na konkrétní obec a rok | Could | nesplněno |
| FR-14 | Portfoliový a filtrovaný pohled | Could | nesplněno |

### 8.2 Nefunkční požadavky (business pohled)

| ID | Oblast | Požadavek |
|---|---|---|
| NFR-01 | Přístup | Přihlášení firemní identitou (SSO / Entra ID), role-based přístup. Sdílené heslo je nepřípustné. |
| NFR-02 | Auditovatelnost | Log přístupů (kdo, kdy, jakou obec zobrazil) po dobu danou interní politikou. |
| NFR-03 | Aktualizace dat | Roční přepočet po zveřejnění výkazů za uzavřený rok; jasně komunikované datum poslední aktualizace. |
| NFR-04 | Dostupnost | Interní nástroj, dostupnost v pracovní době, RTO/RPO dle klasifikace (navrhováno: nekritická aplikace). |
| NFR-05 | Výkon | Odezva vyhledání a vykreslení do 3 s. |
| NFR-06 | Umístění dat | Data i aplikace výhradně v infrastruktuře banky. Provoz na veřejném Streamlit Cloud / GitHub Codespaces je vyloučen. |
| NFR-07 | Jazyk | Uživatelské rozhraní v češtině, terminologie sjednocená s metodikou. |
| NFR-08 | Reprodukovatelnost | Ze zveřejněného skóre musí být možné zpětně odvodit vstupní data a verzi metodiky. |
| NFR-09 | Dokumentace metodiky | Písemná, schválená a verzovaná metodika ukazatelů, vah a prahů. |

---

## 9. Klíčová zjištění z analýzy převzatého řešení

Následující zjištění mají **přímý business dopad**. Protože aplikace již produkuje výstupy předávané klientům, nejde o rizika budoucí, ale o rizika **realizovaná**. Technický detail je v [docs/technicka-specifikace.md](docs/technicka-specifikace.md).

| # | Zjištění | Business dopad | Závažnost |
|---|---|---|---|
| Z1 | Obec s **provozním schodkem** dostává v ukazateli s nejvyšší vahou (20 %) **maximálních 10 bodů**. Týká se 498 řádků u ukazatele č. 5 a 542 řádků u ukazatele č. 6. | Nejhorší hospodaření je odměněno nejlepším hodnocením. **Analýza předaná obci ji může utvrdit, že si investici může dovolit, i když je v provozním schodku** – přesně to je deklarovaný účel nástroje. | **Kritická** |
| Z2 | Vyhledávání podle názvu vybere **první shodu bez upozornění**. V datech je 591 duplicitních názvů obcí (např. „Nová Ves“ 14×, „Petrovice“ 9×); dotaz „Lhota“ odpovídá 65 obcím. | Uživatel může v dobré víře analyzovat jinou obec, než zamýšlel, a učinit rozhodnutí na základě cizích čísel. | **Kritická** |
| Z3 | IČO je uloženo jako číslo, tj. bez úvodních nul (11 916 z 12 494 záznamů má 6 místo 8 znaků). | Uživatel, který zkopíruje oficiální IČO „00035513“, dostane „obec nenalezena“. | Vysoká |
| Z4 | **Inflace skóre**: medián 7,6 z 10; 87 % obcí má skóre ≥ 5. | Nástroj slabě rozlišuje v horní části škály – většina obcí vypadá „dobře“. Snížená použitelnost pro triage. | Vysoká |
| Z5 | Dva z dvanácti ukazatelů mají **nulovou váhu**, ale zobrazují se včetně bodů. | Uživatel předpokládá, že se započítávají. Nedorozumění v komunikaci s klientem. | Vysoká |
| Z6 | Ukazatel „Krytí kapitálových výdajů investičními transfery“ dosahuje hodnot až **334 544 300 %** (technický obchvat dělení nulou). | Nesmyslné hodnoty v tabulce zobrazené klientovi/kolegovi. | Vysoká |
| Z7 | Vyhledávací pole interpretuje vstup jako regulární výraz – zadání znaku `(` **shodí aplikaci**. | Běžný uživatel narazí na chybovou obrazovku (např. při vložení „Nová Ves (Praha-východ)“). | Vysoká |
| Z8 | Datovou pipeline **nelze spustit** – obsahuje absolutní cesty ze dvou soukromých počítačů autorů. | Data nelze aktualizovat ani přepočítat; nástroj je zamrzlý na rocích 2024–2025. | **Kritická** |
| Z9 | Uložený soubor `percentiles.pkl` byl vygenerován **starší verzí kódu** (obsahuje neexistující názvy sloupců). | Data v repozitáři nejsou konzistentní s kódem; nelze prokázat, jak vznikla. | Vysoká |
| Z10 | Autentizace jedním sdíleným heslem, bez identity, bez auditu, bez omezení počtu pokusů. | Nesplňuje bezpečnostní standardy banky, není auditovatelné. | **Kritická** |
| Z11 | Desktopová varianta (`GUI.py`) čte soubor, který v repozitáři není; webová varianta vyžaduje konfiguraci hesla, která v repozitáři také není. | **Ani jedna z aplikací se z převzatého stavu nespustí.** | **Kritická** |
| Z12 | Peer skupina je definována **pouze počtem obyvatel**, bez ohledu na kraj, typ obce (obec / město / statutární město) či rozsah přenesené působnosti. | Obec s rozšířenou působností je porovnávána s obcí bez ní, přestože mají odlišnou strukturu rozpočtu. | Střední |
| Z13 | U kategorií nad 50 000 obyvatel je v peer skupině 1–12 subjektů. | U největších klientů je srovnání statisticky nepodložené. | Střední |
| Z14 | Chybí jakékoli testy, validace a rekonciliace vůči zdroji. | Není doloženo, že výpočty odpovídají metodice. | Vysoká |
| Z15 | Licence MIT je vedena na soukromou osobu (rok 2026). | Nevyjasněné vlastnictví duševního vlastnictví. | Vysoká |
| Z16 | Ukazatel „Daň z nemovitosti“ je **absolutní částka v Kč**, nikoli poměrový ukazatel; medián se mezi kategoriemi liší o 4 řády. | Pro klienta neinterpretovatelné. **Nezávisle potvrzeno byznysem – viz CR-02.** | Vysoká |
| Z17 | Kód i distribuční kanál (`.exe` v GitHub Releases dle README) leží na **soukromém GitHub účtu** mimo kontrolu banky. Bankovní repozitář nemá žádnou historii. | Banka nemá kontrolu nad artefaktem, jehož výstupy předává klientům. Shadow IT. | **Kritická** |
| Z18 | Článek ČS uvádí „data všech **6 258** obcí“, dataset obsahuje **6 247** obcí na rok. Obce bez rozvahových dat jsou **tiše vyřazeny** a uživatel dostane pouze „obec nenalezena“. | Veřejně komunikované tvrzení neodpovídá datům; bankéř nerozliší překlep od chybějících dat. | Vysoká |
| Z19 | Jediný autor kódu odešel ke konkurenci; byznys vlastníci si do kódu netroufají zasáhnout; **spolu s kódem nebyla předána žádná psaná metodika** (zda existuje jinde, není ověřeno – viz otázka Q3). | Bus factor 0 u nástroje, na kterém stojí desítky klientských projektů ročně. | **Kritická** |

---

## 10. Governance, model risk a compliance

* **Charakter nástroje.** Finální skóre je deterministický bodovací model, nikoli rating a nikoli AI model. Přesto svou podobou (0–10, „skóre“) rating připomíná.
* **Výstupy již jdou klientům.** Podle článku ČS má analýza sloužit jako „pevný podklad pro strategická a politická rozhodnutí“ vedení obcí a jako „vstupní diagnostika“ před navazujícími službami banky. Kombinace nálezů Z1 a Z4 tedy není teoretické riziko – výstup může obec utvrdit v investici, na kterou nemá.
* **Povinné označení.** Ve všech výstupech musí být uvedeno: *„Indikativní podpůrný nástroj. Nenahrazuje úvěrovou analýzu ani rating a nesmí být jediným podkladem pro rozhodnutí o investici či financování.“*
* **Vlastník metodiky.** Byznys vlastníkem je Michal Jeník (Infrastrukturní poradenství). Role však není formalizována a metodika nebyla při předání doložena žádným dokumentem – viz Z19.
* **Model risk.** Pokud má skóre sloužit jako podklad pro rozhodnutí klienta o investici nebo vstupovat do úvěrového procesu, je nutné jej podrobit interním pravidlům pro řízení modelového rizika (validace, dokumentace, periodický backtest).
* **Ochrana osobních údajů.** Vstupní data jsou veřejná data MF ČR o právnických osobách – GDPR se prakticky neuplatňuje. Byznys potvrdil, že aplikace **nepoužívá žádná interní data ČS**. Citlivé je až odvozené hodnocení, které je know-how banky.
* **Sdílení s klientem.** Už probíhá. Nutno rozhodnout, zda a za jakých podmínek pokračovat do vyřešení Z1, Z2 a Z6.
* **Veřejné zpřístupnění.** Pod článkem ČS padl dotaz zastupitele Olomouce, zda bude aplikace veřejně dostupná; odpověď zněla, že forma nabídky klientům se teprve zvažuje. **Doporučení: veřejnou variantu neotevírat, dokud není metodika validována.**

---

## 11. Otevřené otázky pro business

| # | Otázka | Adresát | Stav |
|---|---|---|---|
| O1 | Je Finální skóre určeno jen pro orientaci, nebo má vstupovat do úvěrového procesu? Od toho se odvíjí režim model governance. | Risk / Metodika | otevřeno – výstupy již dnes jdou klientovi |
| O2 | Kdo je vlastníkem metodiky a kdo schvaluje váhy a pevné prahy? | Segment veřejného sektoru | **částečně zodpovězeno** – fakticky M. Jeník, role není formalizována |
| O3 | Mají ukazatele č. 2 a č. 12 dostat váhu, nebo je označíme jako informativní? | Metodika | otevřeno – souvisí s CR-02 |
| O4 | Jak řešit obce s provozním schodkem (Z1) – přiřadit 0 bodů, nebo hodnotu neuvádět? | Metodika | otevřeno – **nejvyšší priorita** |
| O5 | Má se peer skupina rozšířit o kraj / typ obce (Z12)? | Metodika | otevřeno |
| O6 | Kolik let historie má být dostupných (dnes 2)? | Business | otevřeno – blokuje CR-01 |
| O7 | Jak často se má provádět přepočet a kdo za něj odpovídá? | Provoz | **zodpovězeno** – 1× ročně, březen–duben; odpovědnost přechází na Engineering |
| O8 | Kdo má mít přístup (role, útvary) a je potřeba four-eyes u exportů? | Compliance | otevřeno |
| O9 | Je vyjasněno vlastnictví duševního vlastnictví k převzatému kódu a metodice (Z15)? | Legal | otevřeno – **zostřeno**, autor je u konkurence |
| O10 | Existuje autoritativní zdroj pro rekonciliaci (např. vlastní výpočet metodika na vzorku 20 obcí)? | Metodika | otevřeno |
| O11 | Kterým obcím již byla analýza předána a přepočítávají se po opravě metodiky? | Byznys vlastník | otevřeno |
| O12 | Pokračuje se výdej nových klientských analýz do vyřešení Z1 a Z2? | Byznys vlastník + Risk | otevřeno – **rozhodnout neprodleně** |
| O13 | Uvažuje se stále o veřejném zpřístupnění aplikace? | Byznys vlastník | otevřeno |

Další provozní a technické otázky na byznys vlastníka jsou v [docs/prevzeti-provoz-a-backlog.md](docs/prevzeti-provoz-a-backlog.md), kap. 9.

---

## 12. Akceptační kritéria

Řešení lze považovat za připravené k pilotnímu provozu, pokud:

1. **A1** – Vyhledání podle IČO funguje pro standardní osmimístný tvar včetně úvodních nul (FR-02).
2. **A2** – Při více shodách názvu se zobrazí seznam k výběru; nikdy se automaticky nezvolí jedna z více obcí (FR-03).
3. **A3** – Žádný vstup do vyhledávacího pole nezpůsobí chybovou obrazovku (Z7).
4. **A4** – Metodika je písemně schválena vlastníkem, včetně řešení Z1, Z4, Z5 a Z6.
5. **A5** – Na vzorku minimálně 20 obcí napříč kategoriemi je hodnota všech 12 ukazatelů rekonciliována s nezávislým výpočtem metodika; odchylka 0.
6. **A6** – Datovou pipeline lze spustit z čistého prostředí bez zásahu do zdrojového kódu a výsledek je bit-shodný při opakovaném běhu (Z8, Z9).
7. **A7** – Přihlášení probíhá firemní identitou; sdílené heslo je odstraněno; přístupy jsou logovány (NFR-01, NFR-02).
8. **A8** – Aplikace i data běží v infrastruktuře banky (NFR-06).
9. **A9** – V UI je viditelné datum dat, verze metodiky a povinné upozornění dle kap. 10.
10. **A10** – Existuje automatizovaná testovací sada pokrývající výpočet ukazatelů a bodování (Z14).

---

## 13. Doporučený postup

| Fáze | Obsah | Výstup |
|---|---|---|
| **F0 – Zjištění stavu a rozhodnutí o rizikách** | Schůzka s byznys vlastníkem: získat vstupní data z MONITORu, popis dnešního provozu a metodiku. Prezentovat Z1 a Z2 a rozhodnout, zda se do opravy pokračuje ve výdeji nových klientských analýz. | Rozhodnutí o řízení rizika, kompletní předání |
| **F1 – Stabilizace** | Zprovoznit pipeline (Z8), opravit Z2, Z3, Z7, Z11, doplňovat upozornění dle kap. 10. Přenést kód do bankovního repozitáře (Z17). | Spustitelné a reprodukovatelné řešení |
| **F2 – Metodika** | Vyřešit Z1, Z4, Z5, Z6, Z12, Z13. Realizovat CR-02 a CR-03 včetně kvantifikace dopadu. Schválit dokument metodiky. Rekonciliace dle A5. | Schválená metodika v1.0 |
| **F3 – Roční přepočet** | Realizovat CR-01 (data k 12/2026) v okně březen–duben. Nahradit `pickle` bezpečným formátem, doplnit testy (Z14). | Reprodukovatelný roční přepočet |
| **F4 – Zoficiálnění** | SSO, audit log, monitoring, SLA, provozní dokumentace, předání do správy ITRP. | Produkční aplikace s vlastníkem |

> **F0 nesnáší odklad.** Aplikace už běží a už produkuje výstupy pro klienty. Kombinace Z1 (schodek = 10 bodů) a Z2 (záměna obce) znamená, že každá další vydaná analýza nese riziko, o kterém byznys zatím neví.
> Zároveň platí, že **CR-01 má tvrdý termín** – pokud pipeline nebude spustitelná do března, roční aktualizace dat k 12/2026 se nestihne a hlavní služba týmu se zastaví.

---

## 14. Slovník pojmů

| Pojem | Význam |
|---|---|
| **MONITOR** | Informační portál Ministerstva financí ČR s výkazy územních samosprávných celků. |
| **FIN 2-12 M** | Výkaz pro hodnocení plnění rozpočtu územních samosprávných celků. |
| **Rozvaha (ROZV)** | Účetní výkaz aktiv a pasiv obce. |
| **Rozpočtová skladba** | Vyhláškou daná číselníková struktura příjmů (třídy 1–4) a výdajů (třídy 5–6). |
| **Peer skupina** | Skupina srovnatelných obcí – zde obce stejné velikostní kategorie v témže roce. |
| **Pravidlo rozpočtové odpovědnosti** | Poměr dluhu obce k průměru jejích příjmů za předchozí 4 roky (zákon č. 23/2017 Sb.). |
| **Percentil / decil** | Hranice, pod kterou leží daný podíl obcí v peer skupině. |
| **IQR** | Mezikvartilové rozpětí; zde se používá k vyloučení odlehlých hodnot. |
| **Finální skóre** | Vážený součet bodů za 12 ukazatelů, rozsah 0–10. |
