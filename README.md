# WIN4SMEs — Innowacje w miejscu pracy

Czytelny podręcznik HTML opracowany na podstawie dokumentacji WP4.1 / A4.1 oraz trzech szkolnych scenariuszy zajęć.

## Zawartość

- 18 stron HTML: przewodnik, program, siedem modułów, wdrożenie w ZSZ5, bibliografia, biblioteka i pełne teksty dokumentów.
- 15 plików źródłowych, dostępnych także do pobrania ze strony.
- Pełna treść scenariuszy szkolnych 1–3 bez redakcyjnych zmian, wraz z tabelami.
- Mapa dwóch numeracji: szkolny moduł 3 odpowiada modułowi 4 pełnego programu.
- Osobne uwagi o czasie zajęć, brakujących materiałach i statusie źródeł.

Scenariusze są materiałami do realizacji zajęć. Zbiór nie zawiera raportu z przeprowadzonego pilotażu.

## Uruchomienie

Strona jest statyczna i nie wymaga JavaScriptu w przeglądarce. Gotowe pliki znajdują się w `public/`.

```sh
npm run dev
```

Podgląd: `http://127.0.0.1:4173`.

```sh
npm run build
```

Polecenie tworzy katalog `dist/`, gotowy do hostingu statycznego. Build i serwer używają wyłącznie standardowej biblioteki Node.js. Zależności startowego szablonu Sites zachowano w repozytorium; statyczna strona nie ładuje ich u czytelnika.

## Ponowne opracowanie źródeł

```sh
python3 -m pip install -r requirements.txt
python3 scripts/prepare.py
npm run build
```

`scripts/prepare.py` konwertuje DOCX z zachowaniem list, tabel, przypisów i obrazów, a następnie sprawdza obecność akapitów tekstu głównego oraz tabel w tej samej kolejności. Konwersja trzech szkolnych scenariuszy przerywa się przy pominięciu lub przestawieniu akapitu. `conversion-report.json` zawiera wynik porównania i ostrzeżenia formatowania konwertera. `public/manifest.json` zawiera sumy SHA-256 wszystkich 15 oryginałów.

`content/wdrozenie.md` jest opracowaniem redakcyjnym. Pozostałe materiały wejściowe są w `sources/`. Oryginały DOCX i PDF pozostają niezmienione.

## Autorstwo i zakres

Program międzynarodowy: Hanse-Parlament, listopad 2025. Dokument „myśl innowacyjnie”: Wiesław Filipiak i Maciej Najwer, Zespół Szkół Zawodowych nr 5 we Wrocławiu, styczeń 2026. Opracowanie internetowe: wrzesień 2026.

Bibliografia i oceny wiarygodności odtwarzają opracowanie znajdujące się w folderze projektu; nie stanowią nowego audytu internetowego. Publiczna dostępność repozytorium nie zmienia praw do dokumentów ani zewnętrznych materiałów cytowanych w źródłach.

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Education and Culture Executive Agency (EACEA). Neither the European Union nor EACEA can be held responsible for them.
