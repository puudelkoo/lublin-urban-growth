# Rozwój zabudowy i zmiany terenów zielonych w Lublinie w latach 2006–2026

[English version](README.md)

## Opis projektu

Projekt przedstawia analizę zmian pokrycia terenu oraz rozwoju zabudowy w Lublinie w latach 2006–2026 z wykorzystaniem zobrazowań satelitarnych Landsat, Google Earth Engine oraz narzędzi Python GIS.

Analiza została wykonana dla trzech lat referencyjnych:

- 2006,
- 2016,
- 2026.

Głównym celem projektu było określenie, jak w ciągu 20 lat zmieniała się przestrzenna struktura Lublina, ze szczególnym uwzględnieniem wzrostu powierzchni zabudowanych oraz zmian powierzchni sklasyfikowanych jako roślinność.

Analiza obejmuje zarówno całe miasto, jak i jego 27 dzielnic.

Pokrycie terenu zostało podzielone na cztery klasy:

- **vegetation** — roślinność,
- **built-up** — tereny zabudowane,
- **other** — pozostałe powierzchnie,
- **water** — woda.

---

## Cele projektu

Najważniejsze cele analizy:

- przygotowanie porównywalnych kompozytów Landsat dla lat 2006, 2016 i 2026,
- obliczenie wskaźników spektralnych NDVI i NDBI,
- przeprowadzenie eksploracyjnej analizy K-means,
- wykonanie nadzorowanej klasyfikacji pokrycia terenu przy użyciu Random Forest,
- ocena jakości klasyfikacji,
- identyfikacja zmian pokrycia terenu pomiędzy analizowanymi okresami,
- określenie powierzchni nowo sklasyfikowanych terenów zabudowanych,
- analiza zmian powierzchni roślinności,
- porównanie zmian pomiędzy dzielnicami Lublina,
- przygotowanie tabel, map i wykresów podsumowujących wyniki.

---

## Obszar analizy

Obszarem badań jest administracyjny obszar miasta **Lublin, Polska**.

Granica miasta została utworzona poprzez połączenie oficjalnych granic 27 dzielnic Lublina.

Powierzchnia otrzymanego obszaru miasta wynosi około:

**147,48 km²**

Granice administracyjne były również wykorzystywane do wykonania statystyk przestrzennych dla poszczególnych dzielnic.

---

## Dane

### Dane satelitarne

W projekcie wykorzystano dane **Landsat Collection 2 Level-2 Surface Reflectance** dostępne w Google Earth Engine.

Dla poszczególnych lat wykorzystano:

| Rok | Sensor | Kolekcja Google Earth Engine |
|---|---|---|
| 2006 | Landsat 5 TM | `LANDSAT/LT05/C02/T1_L2` |
| 2016 | Landsat 8 OLI | `LANDSAT/LC08/C02/T1_L2` |
| 2026 | Landsat 8 OLI | `LANDSAT/LC08/C02/T1_L2` |

W każdym roku wykorzystano obserwacje z okresu letniego:

**1 czerwca – 31 sierpnia**

Zastosowanie tego samego sezonu ogranicza wpływ sezonowości roślinności na porównanie wyników pomiędzy latami.

### Granice administracyjne

Granice dzielnic pochodzą z oficjalnych danych GIS miasta Lublin.

Dane wejściowe zapisano w układzie:

**ETRS89 / Poland CS2000 zone 8 — EPSG:2179**

Na potrzeby Google Earth Engine geometrie były następnie transformowane do **EPSG:4326**.

---

## Technologie

Projekt został wykonany z wykorzystaniem:

- Python,
- Google Earth Engine Python API,
- geemap,
- GeoPandas,
- pandas,
- NumPy,
- Matplotlib,
- scikit-learn,
- Jupyter Notebook,
- Visual Studio Code.

---

## Metodyka

### 1. Przygotowanie granicy miasta

Oficjalne granice dzielnic Lublina zostały połączone przy użyciu operacji `dissolve`, tworząc pojedynczą geometrię reprezentującą obszar miasta.

Poprawność granicy zweryfikowano poprzez porównanie powierzchni wszystkich dzielnic z powierzchnią otrzymanej granicy miasta.

---

### 2. Przygotowanie danych Landsat

Dla każdego roku wykonano:

- filtrowanie zobrazowań do granic Lublina,
- filtrowanie do okresu letniego,
- maskowanie chmur,
- maskowanie cieni chmur,
- maskowanie śniegu,
- maskowanie pikseli nasyconych radiometrycznie,
- skalowanie wartości Surface Reflectance,
- ujednolicenie nazw pasm pomiędzy Landsat 5 i Landsat 8.

Wspólny zestaw pasm:

- `blue`,
- `green`,
- `red`,
- `nir`,
- `swir1`,
- `swir2`.

Dla każdego roku utworzono następnie **medianowy kompozyt sezonowy**.

---

### 3. Kontrola liczby poprawnych obserwacji

Dla każdego roku sprawdzono liczbę poprawnych obserwacji dostępnych dla poszczególnych pikseli po zastosowaniu masek jakości.

Średnia liczba dostępnych obserwacji wyniosła około:

| Rok | Średnia liczba poprawnych obserwacji |
|---|---:|
| 2006 | 3,72 |
| 2016 | 4,57 |
| 2026 | 3,68 |

W analizowanym obszarze nie występowały piksele całkowicie pozbawione poprawnych obserwacji.

---

### 4. Wskaźniki spektralne

Do kompozytów dodano dwa wskaźniki spektralne.

#### NDVI

Normalized Difference Vegetation Index:

```text
NDVI = (NIR - RED) / (NIR + RED)
```

Wskaźnik wykorzystywany jest do identyfikacji powierzchni pokrytych roślinnością.

#### NDBI

Normalized Difference Built-up Index:

```text
NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
```

Wskaźnik wspiera rozróżnianie powierzchni zabudowanych.

Wskaźniki obliczano przy użyciu wyrażeń matematycznych zamiast funkcji `normalizedDifference`, aby uniknąć automatycznego maskowania ujemnych wartości reflektancji występujących po skalowaniu danych Landsat Collection 2.

---

## Eksploracyjna analiza K-means

Przed wykonaniem klasyfikacji nadzorowanej przeprowadzono eksploracyjną analizę klasteryzacji K-means.

Do analizy wykorzystano połączoną próbę około 15 000 pikseli z trzech analizowanych lat.

Przed klasteryzacją dane zostały standaryzowane.

Sprawdzono wartości `k` od 2 do 8 przy użyciu:

- inertia,
- silhouette score.

Ostatecznie wybrano **k = 4** jako kompromis pomiędzy strukturą danych a planowanym podziałem tematycznym.

Klastry K-means traktowano wyłącznie jako grupy spektralne i nie przypisywano im bezpośrednio klas pokrycia terenu.

---

## Klasyfikacja Random Forest

Końcową klasyfikację wykonano przy użyciu algorytmu **Random Forest**.

Wykorzystano następujące zmienne:

- blue,
- green,
- red,
- nir,
- swir1,
- swir2,
- NDVI,
- NDBI.

Próbki treningowe zostały ręcznie wyznaczone i zapisane jako poligony dla czterech klas:

| Klasa | ID |
|---|---:|
| Vegetation | 0 |
| Built-up | 1 |
| Other | 2 |
| Water | 3 |

Łącznie przygotowano **52 poligony referencyjne**.

Zostały one podzielone na niezależne zbiory treningowe i testowe.

Model Random Forest zawierał:

**200 drzew**

i był trenowany na wspólnej wieloletniej próbie.

Ten sam klasyfikator zastosowano dla 2006, 2016 i 2026 roku, aby zwiększyć spójność czasową wyników i ograniczyć różnice wynikające z trenowania osobnych modeli dla każdego roku.

---

## Walidacja klasyfikacji

Model oceniono na niezależnej próbie testowej.

Otrzymano:

- **Overall Accuracy: 96,09%**
- **Kappa: 0,944**

Macierz pomyłek:

|  | Pred. Vegetation | Pred. Built-up | Pred. Other | Pred. Water |
|---|---:|---:|---:|---:|
| Vegetation | 272 | 2 | 10 | 4 |
| Built-up | 0 | 218 | 4 | 0 |
| Other | 21 | 4 | 125 | 0 |
| Water | 0 | 0 | 0 | 492 |

Najniższą dokładność producenta uzyskano dla klasy **other**, która jest najbardziej zróżnicowana spektralnie i może obejmować m.in. odsłoniętą glebę, powierzchnie rolnicze i suche powierzchnie niezabudowane.

---

# Wyniki

## Zmiany struktury pokrycia terenu

Wyniki wskazują na istotne zmiany struktury pokrycia terenu w Lublinie pomiędzy 2006 i 2026 rokiem.

Przybliżone powierzchnie klas dla całego miasta wyniosły:

| Klasa | 2006 [km²] | 2016 [km²] | 2026 [km²] |
|---|---:|---:|---:|
| Vegetation | 48,5 | 71,0 | 57,1 |
| Built-up | 51,8 | 53,1 | 59,9 |
| Other | 42,6 | 20,1 | 25,6 |
| Water | 4,5 | 3,3 | 4,9 |

W całym analizowanym okresie widoczny jest wzrost powierzchni klasyfikowanej jako tereny zabudowane.

Zmiany klasy `vegetation` i `other` są bardziej złożone i należy interpretować je ostrożnie ze względu na sezonowość, charakter terenów rolniczych, różnice spektralne oraz rozdzielczość danych Landsat.

![Land-cover composition](outputs/figures/land_cover_composition_2006_2026.png)

---

## Nowo sklasyfikowane tereny zabudowane

Za nową zabudowę uznano piksele, które w roku początkowym nie należały do klasy `built-up`, natomiast w roku końcowym zostały sklasyfikowane jako `built-up`.

Otrzymano:

| Okres | Nowa powierzchnia built-up |
|---|---:|
| 2006–2016 | 11,32 km² |
| 2016–2026 | 15,85 km² |
| 2006–2026 | 19,90 km² |

Wyniki wskazują, że powierzchnia przechodząca do klasy `built-up` była większa w okresie **2016–2026** niż w latach **2006–2016**.

Wartość dla okresu 2006–2026 nie jest sumą dwóch okresów dziesięcioletnich. Jest to bezpośrednie porównanie klasyfikacji z lat 2006 i 2026.

![New built-up and vegetation loss](outputs/figures/new_built_up_vs_vegetation_loss.png)

---

## Zmiany powierzchni zabudowanych według dzielnic

Największy wzrost powierzchni klasy `built-up` pomiędzy 2006 i 2026 rokiem wystąpił m.in. w dzielnicach:

| Dzielnica | Zmiana built-up [km²] |
|---|---:|
| Ponikwoda | +2,39 |
| Sławin | +1,47 |
| Węglin Południowy | +1,32 |
| Felin | +1,29 |
| Czechów Północny | +1,00 |
| Szerokie | +0,95 |
| Hajdów-Zadębie | +0,63 |
| Kośminek | +0,41 |
| Głusk | +0,35 |
| Dziesiąta | +0,22 |

Największy wzrost procentowego udziału powierzchni zabudowanych odnotowano między innymi w dzielnicach **Szerokie**, **Węglin Południowy** oraz **Ponikwoda**.

![Top built-up growth](outputs/figures/top10_built_up_growth_2006_2026.png)

![District built-up growth](outputs/figures/district_built_up_growth_2006_2026.png)

---

## Porównanie dwóch dekad

Analiza została również wykonana oddzielnie dla okresów:

- 2006–2016,
- 2016–2026.

Pozwala to sprawdzić, czy rozwój zabudowy następował równomiernie w czasie.

W obu okresach silny wzrost widoczny był m.in. na Ponikwodzie, Sławinie, Węglinie Południowym i Felinie.

W latach 2016–2026 wyraźny wzrost pojawił się również m.in. w Zemborzycach, Czechowie Północnym i Abramowicach.

Wyniki wskazują więc zarówno na utrzymywanie się części wcześniejszych stref rozwoju, jak i pojawianie się silniejszych zmian w kolejnych dzielnicach w drugiej dekadzie.

![Built-up growth by decade](outputs/figures/built_up_growth_by_decade.png)

---

## Zmiany roślinności

W analizie zmian piksel sklasyfikowano jako utratę roślinności, jeżeli:

- w roku początkowym należał do klasy `vegetation`,
- w roku końcowym należał do innej klasy.

Powierzchnia takich zmian wyniosła:

| Okres | Vegetation → inna klasa |
|---|---:|
| 2006–2016 | 8,00 km² |
| 2016–2026 | 22,34 km² |
| 2006–2026 | 13,41 km² |

Wartości te nie oznaczają automatycznie trwałej utraty terenów zielonych.

Przejście z klasy `vegetation` do `other` może być związane między innymi ze zmianami sezonowymi, terenami rolniczymi, suchą roślinnością, odsłoniętą glebą lub różnicami klasyfikacyjnymi.

Dlatego najbardziej jednoznacznym sygnałem urbanizacji jest przejście powierzchni do klasy `built-up`, a nie każda zmiana wychodząca z klasy `vegetation`.

---

## Dzielnice ze spadkiem powierzchni vegetation

W bezpośrednim porównaniu 2006–2026 spadek całkowitej powierzchni klasyfikowanej jako `vegetation` wystąpił tylko w części dzielnic.

Największe spadki zaobserwowano m.in. w:

- Głusku,
- Wrotkowie,
- Węglinie Południowym.

![Vegetation decline](outputs/figures/vegetation_decline_2006_2026.png)

![District vegetation loss](outputs/figures/district_vegetation_loss_2006_2026.png)

---

## Najważniejsze wnioski

Analiza wskazuje na wyraźny wzrost powierzchni sklasyfikowanych jako zabudowane w Lublinie pomiędzy 2006 i 2026 rokiem.

Najsilniejsze zmiany nie były równomiernie rozłożone przestrzennie. Szczególnie duży wzrost powierzchni `built-up` widoczny był w części dzielnic położonych poza najbardziej zwartym centrum miasta, m.in. na Ponikwodzie, Sławinie, Węglinie Południowym, Felinie i Szerokim.

Tempo przechodzenia powierzchni do klasy `built-up` było większe w okresie 2016–2026 niż w latach 2006–2016.

Zmiany powierzchni klasyfikowanej jako `vegetation` były bardziej złożone. Nie każda utrata klasy `vegetation` oznacza bezpośrednią urbanizację, ponieważ część zmian zachodziła pomiędzy roślinnością a klasą `other`.

Wyniki pokazują, że połączenie wieloczasowych danych Landsat, klasyfikacji Random Forest, detekcji zmian i statystyk dzielnicowych pozwala skutecznie analizować długoterminowe zmiany przestrzenne miasta.

---

## Ograniczenia analizy

Wyniki należy interpretować z uwzględnieniem kilku ograniczeń.

### Rozdzielczość przestrzenna

Landsat posiada rozdzielczość przestrzenną około **30 m**.

Jeden piksel może więc zawierać jednocześnie kilka typów pokrycia terenu, np. budynek, drogę i roślinność.

### Mixed pixels

Na obszarach miejskich często występują piksele mieszane, co może prowadzić do niejednoznaczności pomiędzy klasami `built-up`, `vegetation` i `other`.

### Różne sensory

Rok 2006 analizowany jest na podstawie Landsat 5 TM, natomiast lata 2016 i 2026 wykorzystują Landsat 8 OLI.

Pasma zostały zharmonizowane pod względem funkcjonalnym, jednak sensory nie są identyczne.

### Charakter klasy `other`

Klasa `other` obejmuje zróżnicowane powierzchnie, takie jak:

- odsłonięta gleba,
- suche powierzchnie,
- część gruntów rolnych,
- inne powierzchnie niepasujące jednoznacznie do pozostałych klas.

Może to zwiększać zmienność tej klasy pomiędzy latami.

### Interpretacja zmian

Wykryte zmiany są zmianami **klasyfikacji pokrycia terenu w danych Landsat**, a nie dokładną ewidencją nowych budynków lub zmian katastralnych.

W szczególności:

- `vegetation → other` nie musi oznaczać trwałego zaniku zieleni,
- `other → built-up` może reprezentować urbanizację, ale wynik ma rozdzielczość 30 m,
- wyników nie należy interpretować jako dokładnej powierzchni zabudowy budynkowej.

---

## Struktura projektu

```text
lublin-urban-growth/
│
├── data/
│   ├── boundaries/
│   │   ├── city/
│   │   └── districts/
│   └── training/
│
├── notebooks/
│   ├── 00_build_city_boundary.ipynb
│   ├── 01_data_preparation.ipynb
│   ├── 02_indices_classification.ipynb
│   ├── 03_change_detection.ipynb
│   └── 04_statistics_visualization.ipynb
│
├── outputs/
│   ├── figures/
│   └── tables/
│
├── src/
│   └── gee_utils.py
│
├── .gitignore
├── requirements.txt
├── README.md
└── README_PL.md
```

---

## Notebooki

### `00_build_city_boundary.ipynb`

Przygotowanie granicy administracyjnej miasta poprzez połączenie granic dzielnic.

### `01_data_preparation.ipynb`

Przygotowanie danych Landsat, kontrola dostępności scen, preprocessing i tworzenie kompozytów.

### `02_indices_classification.ipynb`

Obliczenie NDVI i NDBI, analiza K-means, przygotowanie danych treningowych, trening i walidacja modelu Random Forest.

### `03_change_detection.ipynb`

Klasyfikacja poszczególnych lat oraz analiza przejść pomiędzy klasami pokrycia terenu.

### `04_statistics_visualization.ipynb`

Statystyki dzielnicowe, agregacja wyników, wykresy i mapy końcowe.

---

## Wyniki projektu

Pliki wynikowe znajdują się w katalogu:

```text
outputs/
```

### Tabele

```text
outputs/tables/
├── built_up_growth_by_decade.csv
├── district_change_2006_2016.csv
├── district_change_2006_2026.csv
├── district_change_2016_2026.csv
└── district_landcover_statistics.csv
```

### Wizualizacje

```text
outputs/figures/
├── built_up_growth_by_decade.png
├── district_built_up_growth_2006_2026.png
├── district_vegetation_loss_2006_2026.png
├── land_cover_composition_2006_2026.png
├── new_built_up_vs_vegetation_loss.png
├── top10_built_up_growth_2006_2026.png
└── vegetation_decline_2006_2026.png
```

---

## Uruchomienie projektu

### 1. Sklonowanie repozytorium

```bash
git clone <repository-url>
cd lublin-urban-growth
```

### 2. Utworzenie środowiska wirtualnego

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 4. Autoryzacja Google Earth Engine

Przed pierwszym uruchomieniem wymagane jest konto z dostępem do Google Earth Engine oraz autoryzacja Earth Engine Python API.

### 5. Uruchomienie notebooków

Notebooki należy wykonywać w kolejności:

```text
00_build_city_boundary.ipynb
01_data_preparation.ipynb
02_indices_classification.ipynb
03_change_detection.ipynb
04_statistics_visualization.ipynb
```

Każdy notebook wykorzystuje wyniki przygotowane na wcześniejszych etapach analizy.

---

## Reprodukowalność

Powtarzalne elementy przetwarzania Google Earth Engine zostały przeniesione do:

```text
src/gee_utils.py
```

Moduł zawiera funkcje odpowiedzialne między innymi za:

- preprocessing Landsat 5,
- preprocessing Landsat 8,
- obliczanie NDVI i NDBI,
- tworzenie kompozytów,
- podział danych referencyjnych,
- ekstrakcję próbek treningowych.

Pozwala to ograniczyć duplikację kodu i zachować spójną metodologię pomiędzy notebookami.

---

## Możliwe dalsze rozwinięcia

Projekt można w przyszłości rozszerzyć między innymi o:

- wykorzystanie Sentinel-2 do walidacji najnowszej klasyfikacji,
- analizę większej liczby lat pośrednich,
- dokładniejszą klasyfikację typów zabudowy,
- analizę zmian na poziomie osiedli lub regularnej siatki,
- połączenie zmian pokrycia terenu z danymi demograficznymi,
- analizę dostępności terenów zielonych,
- analizę temperatury powierzchniowej i efektu miejskiej wyspy ciepła,
- publikację wyników w interaktywnej aplikacji Web GIS.

---



Projekt portfolio GIS / Remote Sensing wykonany z wykorzystaniem danych Landsat, Google Earth Engine i Python.
