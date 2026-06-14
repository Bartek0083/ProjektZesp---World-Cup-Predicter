# World Cup Predictor

World Cup Predictor to aplikacja webowa do analizowania reprezentacyjnych meczów piłkarskich, symulowania przebiegu spotkań oraz sprawdzania możliwych scenariuszy fazy grupowej i pucharowej mistrzostw świata. Projekt łączy model machine learningu, backend FastAPI oraz interaktywny frontend działający jako jedna aplikacja na jednym porcie.

## Spis Treści

- [Cel Projektu](#cel-projektu)
- [Geneza I Zakres Prac](#geneza-i-zakres-prac)
- [Najważniejsze Funkcje](#najważniejsze-funkcje)
- [Jak Działa Symulacja Meczu](#jak-działa-symulacja-meczu)
- [Technologie](#technologie)
- [Uruchomienie Aplikacji](#uruchomienie-aplikacji)
- [Jak Korzystać Z Aplikacji](#jak-korzystać-z-aplikacji)
- [Model Machine Learningu](#model-machine-learningu)
- [API](#api)
- [Struktura Projektu](#struktura-projektu)
- [Dane I Artefakty](#dane-i-artefakty)

## Cel Projektu

Celem aplikacji jest pokazanie, jak dane rankingowe FIFA można wykorzystać do przewidywania wyników meczów oraz budowania pełnych scenariuszy turniejowych. Użytkownik może:

- porównać dwie reprezentacje i zobaczyć prawdopodobieństwa zwycięstwa lub remisu,
- uruchomić animowaną symulację meczu z licznikiem minut, bramkami, dogrywką i karnymi,
- symulować grupy mistrzostw świata i analizować awans drużyn,
- sprawdzić najlepsze drużyny z trzecich miejsc,
- przeprowadzić fazę pucharową i zobaczyć drabinkę turnieju.

## Geneza I Zakres Prac

Projekt składa się z dwóch uzupełniających się części. Główna aplikacja odpowiada za model machine learningu, predykcję wyniku, symulację grup oraz symulację turnieju. Szczegółowa symulacja meczu powstała pierwotnie jako osobny moduł, a w obecnej wersji została przeniesiona do głównego projektu i działa bez uruchamiania dodatkowego serwera.

| Obszar | Zakres |
| --- | --- |
| Główna aplikacja | backend FastAPI, model ML, predykcja meczu, symulacja grup, symulacja turnieju, frontend i integracja widoków |
| Moduł symulacji meczu | silnik minutowy, tablica wyniku, licznik meczu, boisko, relacja na żywo, dogrywka, złota bramka i rzuty karne |

Zakres prac zespołu:

- Bartłomiej Muranowicz - główna aplikacja, model ML, predykcja wyników, symulacja fazy grupowej, symulacja turnieju oraz integracja widoków,
- Jakub Szych - pierwotny moduł minutowej symulacji meczu, silnik `match_engine.py`, widok tablicy wyniku, boisko, relacja na żywo i zasady pucharowe.

Dzięki integracji użytkownik nie musi przełączać się między osobnymi aplikacjami. Predykcja, symulacja meczu, grupy i turniej są dostępne z jednego interfejsu pod adresem `http://127.0.0.1:8011/`.

## Najważniejsze Funkcje

### Predykcja Meczu

Zakładka `Mecz` pozwala wybrać gospodarza, gościa oraz informację, czy spotkanie jest rozgrywane na neutralnym terenie. Po kliknięciu `Oblicz` aplikacja pokazuje procentowe szanse:

- zwycięstwa gospodarzy,
- remisu,
- zwycięstwa gości.

Wyniki są prezentowane w czytelnych paskach procentowych z flagami drużyn.

### Live Symulacja Meczu

Pod predykcją znajduje się moduł `Symulacja meczu`. Pozwala on przeprowadzić spotkanie minuta po minucie:

- wynik aktualizuje się na tablicy meczowej,
- licznik pokazuje aktualną minutę,
- bramki pojawiają się dopiero wtedy, gdy symulowany czas do nich dojdzie,
- relacja live rozdziela zdarzenia gospodarzy i gości wizualnie na dwie strony,
- boisko pokazuje znaczniki bramek w czasie meczu,
- tryb turniejowy obsługuje dogrywkę, złotą bramkę i rzuty karne,
- karne są pokazane jako zielone lub czerwone kółka pod nazwami drużyn.

### Symulacja Grup

Zakładka `Grupy` służy do pracy z fazą grupową:

- wyświetla grupy w tabelach,
- pozwala edytować skład grup przez kliknięcie drużyny,
- uruchamia wiele symulacji meczów grupowych,
- pokazuje procentowe szanse awansu,
- wyróżnia drużyny najczęściej awansujące,
- analizuje ranking drużyn z trzecich miejsc,
- pozwala przejść do podglądu układu 1/16 finału.

### Symulacja Turnieju

Zakładka `Turniej` prezentuje fazę pucharową:

- pokazuje drabinkę mistrzostw,
- pozwala symulować wiele przebiegów turnieju,
- wskazuje faworytów do mistrzostwa,
- może korzystać z drużyn wybranych na podstawie ostatniej symulacji grup,
- prezentuje ścieżkę od 1/16 finału do finału.

## Jak Działa Symulacja Meczu

Symulacja meczu nie jest tylko losowym wypisaniem końcowego wyniku. Silnik buduje przebieg spotkania krok po kroku, a frontend pokazuje zdarzenia dopiero wtedy, gdy dojdzie do nich licznik meczu.

Najważniejsze założenia:

- liczba bramek jest generowana na podstawie siły drużyn,
- minuty bramek są losowane z większą wagą dla drugiej połowy, bo w praktyce wiele meczów otwiera się po przerwie,
- w trybie towarzyskim mecz może skończyć się remisem po 90 minutach,
- w trybie turniejowym można użyć dogrywki, złotej bramki lub karnych bezpośrednio po 90 minutach,
- po rzutach karnych aplikacja pokazuje rozstrzygnięcie pod wynikiem oraz serię karnych w formie zielonych i czerwonych kółek,
- opisy bramek są zróżnicowane, żeby relacja live przypominała krótką transmisję tekstową, a nie powtarzający się komunikat.

Mechanizm symulacji uzupełnia model ML. Model odpowiada za ocenę szans `1X2`, a silnik meczowy odpowiada za pokazanie, jak takie spotkanie mogłoby przebiegać minuta po minucie.

## Technologie

Projekt działa jako jedna aplikacja backendowo-frontendowa.

| Warstwa | Technologie |
| --- | --- |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | HTML, CSS, JavaScript |
| Machine learning | scikit-learn, pandas, numpy, joblib |
| Model | Random Forest + kalibracja prawdopodobieństw |
| Dane | CSV z meczami, rankingami FIFA i terminarzem grup |

## Uruchomienie Aplikacji

### 1. Utworzenie środowiska

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalacja zależności

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Start serwera

```powershell
python run_server.py
```

Aplikacja działa pod adresem:

```text
http://127.0.0.1:8011/
```

Dokumentacja API FastAPI jest dostępna pod adresem:

```text
http://127.0.0.1:8011/docs
```

W projekcie używany jest jeden główny port: `8011`.

## Jak Korzystać Z Aplikacji

### Strona Główna

Po wejściu do aplikacji użytkownik widzi landing page ze skrótem najważniejszych modułów. Kliknięcie logo `World Cup Predictor` w lewym górnym rogu wraca do strony głównej.

### Zakładka Mecz

1. Wybierz drużynę gospodarzy.
2. Wybierz drużynę gości.
3. Ustaw, czy mecz jest rozgrywany na neutralnym terenie.
4. Kliknij `Oblicz`.
5. Sprawdź procentowe szanse wyniku.
6. Użyj panelu `Symulacja meczu`, aby zasymulować przebieg spotkania.

Panel symulacji ma wygląd transmisyjny: tablica wyniku, licznik, boisko, relacja live i podsumowanie są widoczne w jednym miejscu.

### Zakładka Grupy

1. Przejdź do zakładki `Grupy`.
2. Przejrzyj tabele grup.
3. Kliknij drużynę, jeśli chcesz ją zmienić.
4. Ustaw liczbę symulacji.
5. Kliknij `Symuluj grupy`.
6. Sprawdź sekcje `Trzecie miejsca` oraz `Awans z grupy`.
7. Po symulacji możesz wyświetlić podgląd drabinki.

Interfejs został przygotowany tak, aby tabele były czytelne, miały własny scroll i mieściły najważniejsze dane przy standardowej skali przeglądarki.

### Zakładka Turniej

1. Przejdź do zakładki `Turniej`.
2. Sprawdź wstępny rozkład drabinki.
3. Wybierz liczbę symulacji turnieju.
4. Zdecyduj, czy używać drużyn z ostatniej symulacji grup.
5. Kliknij `Symuluj turniej`.
6. Sprawdź faworytów oraz przebieg fazy pucharowej.

Drabinka jest kompaktowa i pokazuje cały układ turniejowy bez potrzeby uruchamiania osobnej aplikacji.

## Model Machine Learningu

Model machine learningu został wprowadzony po to, aby predykcje nie były ręcznie ustawionymi wartościami, ale wynikały z danych historycznych. Aplikacja uczy się zależności pomiędzy siłą drużyn a wynikiem meczu.

Model korzysta między innymi z takich cech:

- ranking FIFA gospodarzy i gości,
- punkty FIFA gospodarzy i gości,
- różnica rankingu,
- różnica punktów,
- informacja o neutralnym terenie,
- typ turnieju.

W projekcie używany jest `RandomForestClassifier` z kalibracją prawdopodobieństw. Dzięki temu aplikacja może nie tylko wskazać najbardziej prawdopodobny wynik, ale też pokazać szanse w formie procentów.

Model przewiduje trzy klasy:

- `home_win` - wygrana gospodarzy,
- `draw` - remis,
- `away_win` - wygrana gości.

Pierwsze wywołanie endpointu trenuje model i zapisuje go do pliku:

```text
artifacts/world_cup_model.joblib
```

Przy kolejnych uruchomieniach aplikacja może wczytać zapisany model, dzięki czemu start jest szybszy.

## API

Najważniejsze endpointy:

| Metoda | Endpoint | Opis |
| --- | --- | --- |
| `GET` | `/health` | Sprawdza, czy backend działa |
| `GET` | `/teams` | Zwraca listę dostępnych drużyn |
| `GET` | `/group-matches` | Zwraca domyślne mecze fazy grupowej |
| `GET` | `/evaluation` | Zwraca metryki modelu |
| `POST` | `/predict-match` | Zwraca prawdopodobieństwa wyniku meczu |
| `POST` | `/simulate-match` | Symuluje przebieg meczu minuta po minucie |
| `POST` | `/simulate-group-stage` | Symuluje fazę grupową |
| `POST` | `/simulate-world-cup` | Symuluje fazę pucharową lub cały turniej |

Przykładowe zapytanie do predykcji meczu:

```powershell
$body = @{
  home_team = "Poland"
  away_team = "Netherlands"
  tournament = "FIFA World Cup"
  neutral = 1
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://127.0.0.1:8011/predict-match" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Struktura Projektu

```text
.
├── api.py                                      # Backend FastAPI i endpointy aplikacji
├── data.py                                     # Wczytywanie i przygotowanie danych
├── model.py                                    # Trenowanie, zapis i użycie modelu ML
├── simulator.py                                # Symulacje grup i fazy pucharowej
├── match_engine.py                             # Minutowa symulacja pojedynczego meczu
├── teams_data.py                               # Fallbackowe ratingi drużyn dla symulacji
├── run_server.py                               # Jeden punkt startu aplikacji na porcie 8011
├── frontend/
│   ├── index.html                              # Struktura interfejsu
│   ├── styles.css                              # Warstwa wizualna i glass morphism
│   ├── app.js                                  # Logika UI i komunikacja z API
│   └── assets/                                 # Grafiki i tło stadionu
├── Groups_Matches_corrected_clean.csv          # Domyślne mecze grup
├── matches_2012_2026_with_fifa_ranking_clean.csv
│                                                # Dane historyczne z rankingami FIFA
└── requirements.txt                            # Zależności Pythona
```

## Dane I Artefakty

Repozytorium korzysta z dwóch głównych plików danych:

- `matches_2012_2026_with_fifa_ranking_clean.csv` - dane historyczne meczów i rankingów FIFA,
- `Groups_Matches_corrected_clean.csv` - domyślny układ meczów grupowych.

Model po treningu jest zapisywany w katalogu:

```text
artifacts/
```

Katalog `.venv/`, pliki `__pycache__/`, pliki `.pyc` oraz logi są ignorowane przez `.gitignore`.

## Status Projektu

Aplikacja jest zintegrowana w jednym backendzie i jednym frontendzie. Moduł symulacji meczu nie wymaga już osobnego serwera, a całość działa przez:

```text
http://127.0.0.1:8011/
```
