# Proxima Nova — pliki fontu

Proxima Nova to font komercyjny (Mark Simonson Studio). **Nie dołączamy go do repozytorium** — wstaw tutaj własne pliki z licencji (np. Adobe Fonts, zakup bezpośredni).

## Wymagane pliki

Skopiuj do tego folderu co najmniej:

- `ProximaNova-Regular.woff2` (oraz opcjonalnie `.woff`)
- `ProximaNova-Bold.woff2` (oraz opcjonalnie `.woff`)

Nazwy muszą dokładnie odpowiadać powyższym — `styles.css` odwołuje się do tych ścieżek.

## Bez plików lokalnych

Jeśli masz Proxima Nova zainstalowaną w systemie (np. przez Adobe Creative Cloud), przeglądarka użyje wersji lokalnej dzięki `local()` w `@font-face`.

W przeciwnym razie UI przełączy się na zapasowe czcionki: Segoe UI → Arial → sans-serif.
