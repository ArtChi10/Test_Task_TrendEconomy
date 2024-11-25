import requests
import sqlite3


def fetch_countries_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Не удалось получить данные с API.")


def initialize_database():
    conn = sqlite3.connect("countries.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            cca2 VARCHAR(2) PRIMARY KEY,
            cca3 VARCHAR(3),
            cioc VARCHAR(3),
            name_common TEXT,
            name_official TEXT,
            capital TEXT,
            region TEXT,
            subregion TEXT,
            area REAL,
            population INTEGER
        )
    """)
    print("Таблица countries создана.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_cca2 VARCHAR(2),
            language TEXT,
            FOREIGN KEY (country_cca2) REFERENCES countries (cca2)
        )
    """)
    print("Таблица languages создана.")

    conn.commit()
    print("Все изменения сохранены.")
    return conn


def insert_or_update_data(conn, countries):
    cursor = conn.cursor()
    for country in countries:
        cca2 = country.get("cca2", "")
        cca3 = country.get("cca3", "")
        cioc = country.get("cioc", "")
        name_common = country.get("name", {}).get("common", "")
        name_official = country.get("name", {}).get("official", "")
        capital = ", ".join(country.get("capital", []))
        region = country.get("region", "")
        subregion = country.get("subregion", "")
        area = country.get("area", 0)
        population = country.get("population", 0)

        rows_updated = cursor.execute("""
            UPDATE countries
            SET 
                cca3 = ?, 
                cioc = ?, 
                name_common = ?, 
                name_official = ?, 
                capital = ?, 
                region = ?, 
                subregion = ?, 
                area = ?, 
                population = ?
            WHERE cca2 = ?
        """, (cca3, cioc, name_common, name_official, capital, region, subregion, area, population, cca2)).rowcount

        if rows_updated == 0:
            cursor.execute("""
                INSERT INTO countries (
                    cca2, cca3, cioc, name_common, name_official, capital, region, subregion, area, population
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cca2, cca3, cioc, name_common, name_official, capital, region, subregion, area, population))
        else:
            cursor.execute("DELETE FROM languages WHERE country_cca2 = ?", (cca2,))
        for language in country.get("languages", {}).values():
            cursor.execute("""
                INSERT INTO languages (country_cca2, language)
                VALUES (?, ?)
            """, (cca2, language))

    conn.commit()

def get_population_of_english_speaking_countries(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(c.population) AS total_population
        FROM countries c
        JOIN languages l ON c.cca2 = l.country_cca2 AND l.language = 'English'
    """)
    result = cursor.fetchone()[0]
    print(f"Сумма популяций стран, где говорят на английском языке: {result}")
    return result


def get_subregions_with_country_count(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.subregion, COUNT(c.cca2) AS country_count
        FROM countries c
        GROUP BY c.subregion
    """)
    result = cursor.fetchall()
    print("Субрегионы и количество стран в каждом:")
    for subregion, count in result:
        print(f"  {subregion}: {count} стран")
    return result

def get_countries_with_multiple_languages(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name_common, GROUP_CONCAT(l.language, ', ') AS languages
        FROM countries c
        JOIN languages l ON c.cca2 = l.country_cca2
        GROUP BY c.cca2
        HAVING COUNT(l.language) > 1
    """)
    result = cursor.fetchall()
    print("Страны с более чем одним языком:")
    for country, languages in result:
        print(f"  {country}: {languages}")
    return result


if __name__ == "__main__":
    API_URL = "https://restcountries.com/v3.1/all"
    CSV_FILE = "countries_data.csv"

    try:
        countries_data = fetch_countries_data(API_URL)
        conn = initialize_database()
        insert_or_update_data(conn, countries_data)
        get_population_of_english_speaking_countries(conn)
        get_subregions_with_country_count(conn)
        get_countries_with_multiple_languages(conn)
        conn.close()
    except Exception as e:
        print(f"Ошибка: {e}")
