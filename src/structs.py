# models.py
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Consumer:
    name: str
    hourly_demand: list[int]  # 24 значения - потребление в каждый час


@dataclass
class Generator:
    name: str
    type: str  # "solar" или "diesel"
    hourly_output: list[int]  # 24 значения - генерация в каждый час
    cost_per_kwh: int  # стоимость за кВт·ч

@dataclass
class TestCase:
    source_file: str
    name: str
    description: str
    consumers: list[Consumer]
    generators: list[Generator]
    
    def total_consumers(self) -> int:
        return len(self.consumers)
    
    def total_generators(self) -> int:
        return len(self.generators)

def load_test_case(filepath: str) -> TestCase:
    """Загружает тестовый случай из JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    name = data.get('name', 'Без названия')
    description = data.get('description', '')
    
    consumers = []
    for c in data.get('consumers', []):
        consumers.append(Consumer(
            name=c['name'],
            hourly_demand=c['hourly_demand']
        ))
    
    generators = []
    for g in data.get('generators', []):
        if g['type'] == 'fixed':
            hourly = [g['constant_output']] * 24
        else:
            hourly = g['hourly_output']
        
        generators.append(Generator(
            name=g['name'],
            type=g['type'],
            hourly_output=hourly,
            cost_per_kwh=g['cost_per_kwh']
        ))
    
    return TestCase(
        source_file=Path(filepath).name, 
        name=name,
        description=description,
        consumers=consumers,
        generators=generators
    )


def validate_consumers_demands(consumers: list[Consumer]) -> bool:
    """Проверяет, что у всех потребителей неотрицательный спрос"""
    for c in consumers:
        if any(d < 0 for d in c.hourly_demand):
            return False
    return True