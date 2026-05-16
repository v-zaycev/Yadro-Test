# main.py
import json
from pathlib import Path
from typing import List
from structs import TestCase, load_test_case
from scheduler import schedule_hour


def run_simulation(test_case: TestCase) -> List[dict]:
    """
    Прогоняет симуляцию для всех 24 часов.
    
    Returns:
        Список словарей с результатами по каждому часу
    """
    results = []
    consumers = test_case.consumers
    generators = test_case.generators
    
    for hour in range(24):
        result = schedule_hour(consumers, generators, hour)
        # Добавляем информацию о часе и суммарных показателях
        result['hour'] = hour
        result['total_demand'] = sum(c.hourly_demand[hour] for c in consumers)
        result['total_generation'] = sum(g.hourly_output[hour] for g in generators)
        results.append(result)
    return results


def print_test_header(test_case: TestCase, file_index: int, total_files: int):
    """Выводит шапку теста"""
    print(f"\n{'=' * 100}")
    print(f"Тест {file_index}/{total_files}: {test_case.name} ({test_case.source_file})")
    if test_case.description:
        print(f"Описание: {test_case.description}")
    print(f"{'=' * 100}")

# main.py (исправленные функции вывода)

def print_test_header(test_case: TestCase, file_index: int, total_files: int):
    """Выводит шапку теста"""
    print(f"\n{'=' * 145}")
    print(f"Тест {file_index}/{total_files}: {test_case.name} ({test_case.source_file})")
    if test_case.description:
        print(f"Описание: {test_case.description}")
    print(f"{'=' * 145}")


def print_hourly_stats_table(results: List[dict]):
    """
    Почасовая статистика: часы по строкам, параметры по столбцам.
    """
    print(f"\n{'=' * 145}")
    print("Почасовая статистика")
    print(f"{'=' * 145}")
    
    # Заголовок
    print(f"{'Час':<6} | {'Стоимость':<10} | {'Спрос':<10} | {'Генерация':<10} | {'Отключено':<10}")
    print("-" * 145)
    
    for r in results:
        print(f"{r['hour']:<6} | {r['cost']:<10} | {r['total_demand']:<10} | {r['total_generation']:<10} | {len(r['off_consumers']):<10} ")
    
    print(f"{'=' * 145}")


def print_generators_schedule(results: List[dict], test_case: TestCase):
    """
    Транспонированная таблица работы генераторов.
    Строки - генераторы, столбцы - часы (0-23).
    1 - генератор включён, 0 - выключен.
    """
    generators = test_case.generators
    n_gens = len(generators)
    n_hours = 24
    
    # Строим матрицу включений
    matrix = [[0] * n_hours for _ in range(n_gens)]
    for hour, r in enumerate(results):
        for gen_idx in r['selected_generators']:
            matrix[gen_idx][hour] = 1
    
    print(f"\n{'=' * 145}")
    print("Расписание работы генераторов (1 - включён, 0 - выключен)")
    print(f"{'=' * 145}")
    
    # Заголовок с часами
    header = f"{'Генератор':<25} | " + " | ".join(f"{h:>2}" for h in range(n_hours))
    print(header)
    print("-" * 145)
    
    # Каждая строка - генератор
    for i, gen in enumerate(generators):
        row = f"{gen.name[:25]:<25} | "
        row += " | ".join(f"{matrix[i][h]:>2}" for h in range(n_hours))
        print(row)
    
    print(f"{'=' * 145}")


def print_consumers_schedule(results: List[dict], test_case: TestCase):
    """
    Транспонированная таблица работы потребителей.
    Строки - потребители, столбцы - часы (0-23).
    1 - потребитель ВКЛЮЧЁН, 0 - отключён.
    """
    consumers = test_case.consumers
    n_cons = len(consumers)
    n_hours = 24
    
    # Строим матрицу включений (1 - включён, 0 - отключён)
    matrix = [[1] * n_hours for _ in range(n_cons)]  # по умолчанию все включены
    for hour, r in enumerate(results):
        for cons_idx in r['off_consumers']:
            matrix[cons_idx][hour] = 0  # отключаем
    
    print(f"\n{'=' * 145}")
    print("Расписание работы потребителей (1 - включён, 0 - отключён)")
    print(f"{'=' * 145}")
    
    # Заголовок с часами
    header = f"{'Потребитель':<25} | " + " | ".join(f"{h:>2}" for h in range(n_hours))
    print(header)
    print("-" * 145)
    
    # Каждая строка - потребитель
    for i, cons in enumerate(consumers):
        row = f"{cons.name[:25]:<25} | "
        row += " | ".join(f"{matrix[i][h]:>2}" for h in range(n_hours))
        print(row)
    
    print(f"{'=' * 145}")


def print_all_reports(results: List[dict], test_case: TestCase, file_index: int, total_files: int):

    print_test_header(test_case, file_index, total_files)
    
    print_hourly_stats_table(results)
    
    print_generators_schedule(results, test_case)
    
    print_consumers_schedule(results, test_case)


def save_results_json(results: List[dict], test_case: TestCase, output_path: str):
    """Сохраняет результаты в JSON файл"""
    consumers = test_case.consumers
    generators = test_case.generators
    
    # Преобразуем индексы в имена для читаемости
    output_data = []
    for r in results:
        output_data.append({
            'hour': r['hour'],
            'total_demand': r['total_demand'],
            'total_generation': r['total_generation'],
            'cost': r['cost'],
            'selected_generators': [generators[i].name for i in r['selected_generators']],
            'off_consumers': [consumers[i].name for i in r['off_consumers']]
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def main():
    test_cases_dir = Path("tests")
    
    if not test_cases_dir.exists():
        print(f"Ошибка: папка '{test_cases_dir}' не найдена")
        return
    
    json_files = list(test_cases_dir.glob("*.json"))
    
    if not json_files:
        print(f"В папке '{test_cases_dir}' нет JSON файлов")
        return
    
    print(f"Найдено тестовых файлов: {len(json_files)}")
    
    for idx, json_file in enumerate(json_files, 1):
        try:
            test_case = load_test_case(str(json_file))
            
            results = run_simulation(test_case)
            
            # Вывод всех отчётов
            print_all_reports(results, test_case, idx, len(json_files))
            
            # Сохранение JSON результата
         #   output_path = json_file.parent / f"{json_file.stem}_output.json"
         #   save_results_json(results, test_case, output_path)
            
        except Exception as e:
            print(f"Ошибка при обработке {json_file.name}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()