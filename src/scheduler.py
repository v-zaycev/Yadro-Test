# solver.py
from src.structs import Consumer, Generator

def min_cost_coverage(
    total_demand: int,
    generators: list[Generator],
    hour: int
) -> tuple[list[int], int]:
    """
    ДП: минимальная стоимость покрытия total_demand.
    
    Args:
        total_demand: суммарный спрос (целое число)
        generators: все генераторы
        hour: час (0-23)
    
    Returns:
        (min_cost, selected_indices)
    """
    max_power = 0
    items = []
    for i, g in enumerate(generators):
        power = g.hourly_output[hour]
        max_power += power
        cost = g.hourly_output[hour] *  g.cost_per_kwh
        items.append((i, power, cost))
    
    if not items:
        return 0, []
    
    INF = 10**18
    costs = [0] + [INF] * (max_power)
    added_mask = [0] * (max_power + 1)
    
    for i, power, cost in items:
        if power == 0:
            continue
        for m in range(max_power, power - 1, -1):
            if costs[m - power] != INF and costs[m - power] + cost < costs[m]:
                costs[m] = costs[m - power] + cost
                added_mask[m] = added_mask[m-power] | (1 << i)

    # Ищем лучший вариант
    best_cost = INF
    best_mask = 0
    for m in range(total_demand, max_power + 1):
        if costs[m] < best_cost:
            best_cost = costs[m]
            best_mask = added_mask[m]
    
    best_indices = [i for i in range(len(generators)) if (best_mask >> i) & 1]

    return best_indices, best_cost


def max_consumers_coverage(
    consumers: list[Consumer],
    generators: list[Generator],
    hour: int
) -> tuple[list[int], list[int], int]:
    """
    Перебор генераторов + жадный выбор потребителей (оптимально для максимизации количества).
    
    Returns:
        (selected_consumer_indices, selected_generator_indices, total_cost)
    """
    max_power = sum([generator.hourly_output[hour] for generator in generators])

    demands = [(int(c.hourly_demand[hour]), i) for i, c in enumerate(consumers)]
    demands.sort()

    total_demand = 0
    total_consumers = 0
    while total_demand + demands[total_consumers][0] < max_power:
        total_demand += demands[total_consumers][0]
        total_consumers += 1

    best_cons = [demands[i][1] for i in range(0, total_consumers)]
    
    best_gens, best_cost  = min_cost_coverage(total_demand, generators, hour)

    return best_cons, best_gens, best_cost


def schedule_hour(
    consumers: list[Consumer],
    generators: list[Generator],
    hour: int
) -> dict:
    """Решает задачу для одного часа"""
    total_demand = sum(c.hourly_demand[hour] for c in consumers)
    total_generation = sum(g.hourly_output[hour] for g in generators)
    
    if total_generation >= total_demand:
        # Режим избытка: всех обеспечиваем
        selected_gens, cost = min_cost_coverage(total_demand, generators, hour)
        return {
            'selected_generators': selected_gens,
            'off_consumers': [],
            'cost': cost
        }
    else:
        # Режим дефицита: максимизируем количество потребителей
        selected_cons, selected_gens, cost = max_consumers_coverage(consumers, generators, hour)
        all_cons = set(range(len(consumers)))
        off_consumers = list(all_cons - set(selected_cons))
        
        return {
            'selected_generators': selected_gens,
            'off_consumers': off_consumers,
            'cost': cost
        }