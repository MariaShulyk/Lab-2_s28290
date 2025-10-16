import numpy as np
import pandas as pd
import random
from faker import Faker
import argparse

# Funkcja, która generuje dane na podstawie numeru studenta
def generate_data(student_number, n_samples=1000):
    np.random.seed(student_number)  # Ustalanie ziarna na podstawie numeru studenta
    random.seed(student_number)
    fake = Faker('pl_PL')
    
    # Listy do losowania cech
    genders = ['Mężczyzna', 'Kobieta']
    education_levels = ['Podstawowe', 'Średnie', 'Wyższe']
    travel_goals = ['Praca', 'Zakupy', 'Edukacja', 'Rozrywka', 'Inne']
    
    # Funkcje pomocnicze do generowania losowych danych
    def random_age():
        return random.randint(18, 70)
    
    def random_salary():
        return round(random.uniform(3000, 15000), 2)
    
    def random_travel_time():
        start_hour = random.randint(5, 23)
        start_minute = random.randint(0, 59)
        duration = random.uniform(0.1, 12)  # Czas trwania podróży (do 12h)
        end_hour = (start_hour + int(duration)) % 24
        end_minute = (start_minute + int((duration % 1) * 60)) % 60
        return f"{start_hour:02}:{start_minute:02}", f"{end_hour:02}:{end_minute:02}"
    
    # Generowanie danych podstawowych
    data = []
    for _ in range(n_samples):
        gender = random.choice(genders)
        age = random_age()
        education = random.choice(education_levels)
        salary = random_salary()
        start_time, end_time = random_travel_time()
        goal = random.choice(travel_goals)
        
        data.append([gender, age, education, salary, start_time, end_time, goal])
    
    df = pd.DataFrame(data, columns=['Płeć', 'Wiek', 'Wykształcenie', 'Średnie Zarobki', 'Czas Początkowy Podróży', 'Czas Końcowy Podróży', 'Cel Podróży'])
    
    # Wprowadzanie błędów w danych (5% braków, 2% niepełnych danych, 2% błędnych czasów)
    n_missing = int(0.05 * n_samples)
    n_partial = int(0.02 * n_samples)
    n_invalid = int(0.02 * n_samples)
    
    # Wprowadzenie braków (losowo wybrane pojedyncze braki)
    for _ in range(n_missing):
        idx = random.randint(0, n_samples - 1)
        col = random.choice(df.columns)
        df.at[idx, col] = np.nan
    
    # Wprowadzenie niepełnych danych (losowo wybrane wiersze z tylko 2 uzupełnionymi kolumnami)
    for _ in range(n_partial):
        idx = random.randint(0, n_samples - 1)
        cols_to_keep = random.sample(list(df.columns), 2)
        for col in df.columns:
            if col not in cols_to_keep:
                df.at[idx, col] = np.nan
    
    # Wprowadzenie błędnych czasów (błędy w czasach startu lub zbyt długi czas podróży)
    for _ in range(n_invalid):
        idx = random.randint(0, n_samples - 1)
        if random.random() < 0.5:
            # Błędny czas startu (np. godzina 25)
            df.at[idx, 'Czas Początkowy Podróży'] = f"{random.randint(24, 30)}:{random.randint(0, 59):02}"
        else:
            # Zbyt długi czas podróży (powyżej 12h)
            df.at[idx, 'Czas Początkowy Podróży'], df.at[idx, 'Czas Końcowy Podróży'] = random_travel_time()
            df.at[idx, 'Czas Końcowy Podróży'] = f"{(int(df.at[idx, 'Czas Początkowy Podróży'].split(':')[0]) + 13) % 24:02}:{random.randint(0, 59):02}"
    
    return df

# Główna funkcja obsługująca argumenty z linii poleceń
if __name__ == "__main__":
    # Konfiguracja argumentów
    parser = argparse.ArgumentParser(description="Generowanie danych podróży na podstawie numeru studenta.")
    parser.add_argument('-s', '--student-number', type=int, required=True, help="Numer studenta (5-cyfrowy).")
    
    args = parser.parse_args()
    
    # Generowanie danych na podstawie numeru studenta
    student_number = args.student_number
    df = generate_data(student_number)
    
    # Zapis do pliku CSV
    filename = f'data_student_{student_number}.csv'
    df.to_csv(filename, index=False)
    
    print(f"Dane zostały wygenerowane i zapisane w pliku '{filename}'")

