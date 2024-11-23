import pandas as pd


def remove_duplicates(file_path, sheet_name, output_file):
    try:
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            print(f"Найдено {duplicates} дубликатов в листе '{sheet_name}'. Удаляем их...")
            data_cleaned = data.drop_duplicates()
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                data_cleaned.to_excel(writer, sheet_name=sheet_name, index=False)
                for sheet in pd.ExcelFile(file_path).sheet_names:
                    if sheet != sheet_name:
                        pd.read_excel(file_path, sheet_name=sheet).to_excel(writer, sheet_name=sheet, index=False)
            print(f"Дубликаты удалены. Файл сохранен как '{output_file}'.")
        else:
            print(f"Дубликатов не найдено в листе '{sheet_name}'.")
        return duplicates
    except Exception as e:
        print(f"Ошибка при удалении дубликатов: {e}")

def fill_base_per(file_path, data_sheet_name, base_period_sheet_name, output_file):
    try:
        data = pd.read_excel(file_path, sheet_name=data_sheet_name)
        base_period = pd.read_excel(file_path, sheet_name=base_period_sheet_name)
        base_period_dict = dict(zip(base_period['UNIT_MEASURE'], base_period['BASE_PER']))
        data['BASE_PER'] = data['UNIT_MEASURE'].map(base_period_dict)
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=data_sheet_name, index=False)
            base_period.to_excel(writer, sheet_name=base_period_sheet_name, index=False)
        print(f"Файл успешно сохранен с заполненной колонкой BASE_PER: {output_file}")
    except Exception as e:
        print(f"Ошибка при заполнении BASE_PER: {e}")


def generate_pivot_table(file_path, sheet_name, output_file):
    try:
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        filtered_data = data[data['BASE_PER'] == "2000"]
        unique_time_periods = filtered_data['TIME_PERIOD'].unique()
        unique_ref_areas = filtered_data['REF_AREA'].unique()
        result_table = pd.DataFrame(index=unique_time_periods, columns=unique_ref_areas)
        for time_period in unique_time_periods:
            for ref_area in unique_ref_areas:
                max_value = filtered_data[
                    (filtered_data['TIME_PERIOD'] == time_period) & (filtered_data['REF_AREA'] == ref_area)
                ]['OBS_VALUE'].max()
                result_table.loc[time_period, ref_area] = max_value
        result_table['Общий итог'] = result_table.max(axis=1)
        result_table.loc['Общий итог'] = result_table.max(axis=0)
        result_table.index = pd.to_numeric(result_table.index, errors='coerce')
        result_table = result_table.sort_index(ascending=True)
        result_table.to_excel(output_file, sheet_name="Pivot_Table")
        print(f"Сводная таблица сохранена в файл: {output_file}")
    except Exception as e:
        print(f"Ошибка при создании сводной таблицы: {e}")


if __name__ == "__main__":
    # Удаление дубликатов
    file_path = "excel_task.xlsx"
    sheet_name = "data"
    output_file = "excel_task_cleaned.xlsx"
    remove_duplicates(file_path, sheet_name, output_file)

    # Заполнение BASE_PER
    file_path = "excel_task_cleaned.xlsx"
    data_sheet_name = "data"
    base_period_sheet_name = "base_period"
    output_file = "excel_task_filled.xlsx"
    fill_base_per(file_path, data_sheet_name, base_period_sheet_name, output_file)

    # Создание сводной таблицы
    file_path = "excel_task_filled.xlsx"
    sheet_name = "data"
    output_file = "pivot_table_output.xlsx"
    generate_pivot_table(file_path, sheet_name, output_file)
