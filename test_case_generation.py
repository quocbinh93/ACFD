from deap import base, creator, tools, algorithms
import random
import pandas as pd
import altair as alt

# Generate test paths using Depth-First Search (DFS)
def generate_test_paths(control_flow_graph):
    def dfs(node, path, visited=None):
        if visited is None:
            visited = set()
        visited.add(node)
        path.append(node)
        if node == "End":
            test_paths.append(path[:])  # Save a copy of the path
        else:
            for next_node in control_flow_graph.get(node, {}).get("next", []):
                if next_node not in visited:  # Avoid cycles
                    dfs(next_node, path[:], visited)
    
    test_paths = []
    if "Root" in control_flow_graph:
        dfs("Root", [])
    return test_paths

# Evaluate a test case by counting the unique transitions it covers
def evaluate_test_case(individual, control_flow_graph):
    covered_transitions = set()
    current_node = "Root"
    for gene in individual:
        next_nodes = control_flow_graph[current_node].get("next", [])
        if gene < len(next_nodes):  # Ensure gene index is valid
            next_node = next_nodes[gene]
            covered_transitions.add((current_node, next_node))
            current_node = next_node
        else:
            break  # Stop if gene index is out of bounds
    return (len(covered_transitions),)  # Return the count of unique transitions as a tuple

# Check if the test paths cover all transitions
def check_coverage(test_paths, control_flow_graph):
    required_transitions = set()
    for node, details in control_flow_graph.items():
        for next_node in details.get("next", []):
            required_transitions.add((node, next_node))
    
    covered_transitions = set()
    for path in test_paths:
        for i in range(len(path) - 1):
            covered_transitions.add((path[i], path[i + 1]))
    
    return required_transitions.issubset(covered_transitions)

def optimize_test_cases(test_paths, control_flow_graph, population_size=50, num_generations=40):
    if not test_paths:
        return []  # Return an empty list if no test paths are available

    # Check initial coverage
    if check_coverage(test_paths, control_flow_graph):
        print("Initial test paths already cover all transitions.")
        return test_paths

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    max_next_length = max((len(v.get("next", [])) for v in control_flow_graph.values() if "next" in v), default=0)

    toolbox.register("attr_int", random.randint, 0, max_next_length - 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=len(max(test_paths, key=len)))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate_test_case, control_flow_graph=control_flow_graph)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=max_next_length - 1, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=population_size)

    for gen in range(num_generations):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))

    best_individuals = tools.selBest(population, k=10)

    # Convert the best individuals to test paths with nodes
    node_keys = list(control_flow_graph.keys())
    best_test_paths = []
    for individual in best_individuals:
        test_path = []
        current_node = "Root"
        for gene in individual:
            next_nodes = control_flow_graph[current_node].get("next", [])
            if gene < len(next_nodes):  # Ensure gene index is valid
                next_node = next_nodes[gene]
                test_path.append(next_node)
                current_node = next_node
            else:
                break  # Stop if gene index is out of bounds
        best_test_paths.append(test_path)

    # Check final coverage
    if check_coverage(best_test_paths, control_flow_graph):
        print("Optimized test paths cover all transitions.")
    else:
        print("Optimized test paths do not cover all transitions.")
    
    return best_test_paths

# Visualize test coverage on the control flow graph
def visualize_test_coverage(optimized_test_cases, control_flow_graph):
    data = []
    for i, test_case in enumerate(optimized_test_cases):
        current_node = "Root"
        for j, gene in enumerate(test_case):
            next_nodes = control_flow_graph[current_node].get("next", [])
            if gene < len(next_nodes):
                next_node = next_nodes[gene]
                data.append({"test_case": f"Test Case {i + 1}", "node": next_node, "order": j + 1})
                current_node = next_node
            else:
                break

    chart = alt.Chart(pd.DataFrame(data)).mark_line(point=True).encode(
        x=alt.X('order:Q', axis=alt.Axis(title='Step Order')),
        y=alt.Y('node:N', axis=alt.Axis(title='Node')),
        color='test_case:N',
        tooltip=['test_case', 'node', 'order']
    ).properties(
        title='Test Case Coverage on Control Flow Graph'
    ).interactive()

    chart.save('test_case_coverage.html')