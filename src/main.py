# main.py
import json
from pathlib import Path
from src.structs import TestCase, load_test_case
from src.scheduler import schedule_hour
from src.output import *

def run_simulation(test_case: TestCase) -> list[dict]:
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
            
            print_all_reports(results, test_case, idx, len(json_files))
            
            
        except Exception as e:
            print(f"Ошибка при обработке {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
