import requests
import csv

def fetch_countries_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Не удалось получить данные с API.")

def process_country_data(countries):
    csv_rows = []
    for country in countries:
        languages = country.get("languages", {})
        if not languages:
            csv_rows.append(format_country_row(country, ""))
        else:
            for language in languages.values():
                csv_rows.append(format_country_row(country, language))
    return csv_rows

def format_country_row(country, language):
    return {
        "cca2": country.get("cca2", ""),
        "cca3": country.get("cca3", ""),
        "cioc": country.get("cioc", ""),
        "name.common": country.get("name", {}).get("common", ""),
        "name.official": country.get("name", {}).get("official", ""),
        "capital": ", ".join(country.get("capital", [])),
        "region": country.get("region", ""),
        "subregion": country.get("subregion", ""),
        "language": language,
        "area": country.get("area", ""),
        "population": country.get("population", ""),
    }

def save_to_csv(file_name, data, fields):
    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    print(f"Данные записаны в файл {file_name}")

if __name__ == "__main__":
    API_URL = "https://restcountries.com/v3.1/all"
    OUTPUT_FILE = "countries_data_with_languages.csv"
    CSV_FIELDS = [
        "cca2", "cca3", "cioc",
        "name.common", "name.official",
        "capital", "region", "subregion",
        "language", "area", "population"
    ]

    try:
        countries_data = fetch_countries_data(API_URL)
        csv_data = process_country_data(countries_data)
        save_to_csv(OUTPUT_FILE, csv_data, CSV_FIELDS)
    except Exception as e:
        print(f"Ошибка: {e}")
