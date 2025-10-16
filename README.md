# Lab2---Obr-bka-danych

### Wymogi do zadania - nie tworzycie nowego repo tylko zmieniacie w nazwe z Lab1 na Lab2 a treść z zadania jeden przenosie na brancha o nazwie zadania!


#### 0. Wasza aplikacja ma automatycznie pobierać i odpalenie skrypt z repozytorium Lab2---Obr-bka-danych przy każdym odpaleniu Waszego Github Action.

#### 1. Stworzenie Google Sheets i dodanie dostępów jako secrety z poziomu GitHub Actions - **3 punkty**

- Student powinien:
  - Stworzyć arkusz Google Sheets, w którym umieści wygenerowane dane w sposób automatyczny.
  - Skonfigurować dostęp do Google Sheets przy użyciu Google API. Klucz API (lub dane uwierzytelniające) powinny zostać umieszczone jako **secret** w repozytorium GitHub.
  - Użyć GitHub Actions do wczytywania danych z Google Sheets, korzystając z zapisanych secretów.

**Kroki**:
- Stworzenie arkusza Google Sheets z danymi.
- Konfiguracja API Google i dodanie danych uwierzytelniających do GitHub Secrets.
- Użycie GitHub Actions do automatycznego pobrania danych z arkusza.

#### 2. Napisanie skryptu czyszczącego dane (usuwanie lub uzupełnianie braków) i standaryzującego dane - **10 punktów**

- Student musi napisać skrypt w Pythonie, który:
  - Odczyta dane z Google Sheets (lub z pliku CSV, jeśli wcześniej pobierze dane).
  - Przeprowadzi czyszczenie danych:
    - **Usuwanie braków** – student może wybrać, które dane zostaną usunięte (np. wiersze z zbyt wieloma brakującymi wartościami).
    - **Uzupełnianie braków** – student może uzupełnić brakujące wartości (np. uzupełnianie medianą, średnią, wartością domyślną itp.).
  - **Standaryzacja danych** – student powinien przeprowadzić standaryzację danych, aby wszystkie zmienne były w odpowiednich jednostkach, np. przekształcić dane na rozkład o średniej 0 i odchyleniu standardowym 1.
  - Zwrócenie czystych danych gotowych do dalszej obróbki.

**Kroki**:
- Odczytanie danych z Google Sheets (lub CSV).
- Czyszczenie danych: usuwanie braków lub uzupełnianie ich, gdy to możliwe.
- Standaryzacja danych.

#### 3. Generowanie raportu z GitHub Actions - **2 punkty**

- Po wykonaniu skryptu czyszczącego i standaryzującego dane, GitHub Actions powinien wygenerować raport, który zawiera:
  - Procent danych, które zostały zmienione w wyniku uzupełniania braków lub standaryzacji.
  - Procent danych, które zostały usunięte w wyniku czyszczenia.
  
**Kroki**:
- Skrypt powinien liczyć zmienione i usunięte dane.
- Na koniec działania skryptu powinien wygenerować raport i zapisać go jako plik tekstowy (np. `report.txt`).
- GitHub Actions powinien wyświetlić zawartość raportu po zakończeniu pracy.

#### 4. Użycie loggera w skrypcie - **3 punkty**

- Skrypt musi zawierać **logger** do śledzenia działań związanych z przetwarzaniem danych:
  - Każdy etap działania skryptu powinien być odpowiednio logowany (np. rozpoczęcie i zakończenie czyszczenia danych, liczba usuniętych wierszy, procent uzupełnionych danych).
  - Logger powinien rejestrować działania w pliku `log.txt` oraz wyświetlać istotne informacje w konsoli (np. liczba zmienionych/uzupełnionych/usuniętych danych).

**Kroki**:
- Skonfiguruj loggera (np. przy użyciu modułu `logging` w Pythonie).
- Zaloguj kluczowe operacje, takie jak odczytanie danych, rozpoczęcie i zakończenie przetwarzania danych, zmiany dokonane w danych itp.

#### 5. Poprawność użycia Gita - **2 punkty**

- Student powinien:
  - Wprowadzać odpowiednio zatytułowane **commity** w repozytorium GitHub (opisujące zmiany w kodzie).
  - Używać **branchy** do wprowadzania większych zmian i zgłaszać pull requesty na główną gałąź (jeśli wymagane).
  - Wszystkie commity muszą być dobrze opisane i reprezentować odpowiednie etapy pracy (np. "Dodanie skryptu czyszczącego dane", "Konfiguracja loggera", "Dodanie raportu z GitHub Actions").

**Kroki**:
- Użycie commita z odpowiednimi opisami zmian.
- Użycie branchy i pull requestów (opcjonalnie, jeśli projekt to wymaga).

### Suma punktów: 20

---

### Podsumowanie zadań

- **Google Sheets i GitHub Secrets** (3 punkty): Konfiguracja dostępu do danych w Google Sheets za pomocą GitHub Actions.
- **Skrypt czyszczący i standaryzujący dane** (10 punktów): Opracowanie skryptu do przetwarzania i standaryzacji danych.
- **Generowanie raportu z GitHub Actions** (2 punkty): Raport dotyczący przetworzonych danych na koniec procesu.
- **Logger** (3 punkty): Użycie loggera do śledzenia działań w skrypcie.
- **Poprawność użycia Gita** (2 punkty): Praca z GitHub zgodnie z dobrymi praktykami (commity, branchy, pull requesty).

###
**Extra 5 punktów:**
- Jeżeli ktoś użyje w organizacji self-hosted runnera.
###
skrypt jest uruchamiany w sposób:

`python3 generator_danych.py -s XXXXX`
