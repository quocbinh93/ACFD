from graphviz import Digraph

def extract_statements(use_case_data):
    statements = []
    for section in ["Main Success Scenario", "Extensions"]:
        for line in use_case_data.get(section, "").strip().split("\n"):
            line = line.strip()
            if line:
                statements.append(line)
    return statements

def analyze_statement(statement):
    statement = statement.upper()
    if "IF" in statement:
        return "condition"
    elif "INPUT" in statement or "ENTER" in statement:
        return "input"
    elif "DISPLAY" in statement or "PRINT" in statement:
        return "output"
    else:
        return "process"

# def acfd(use_case_data):
#     statements = extract_statements(use_case_data)
#     control_flow_graph = {"Root": {"type": "start", "content": "Root Node", "next": []}}
#     current_node = "Root"
#     node_counter = 1

#     for statement in statements:
#         statement_type = analyze_statement(statement)
#         new_node = f"N{node_counter}"
#         control_flow_graph[new_node] = {"type": statement_type, "content": statement, "next": []}
#         node_counter += 1

#         if statement_type == "condition":
#             true_branch_statement = next((s for s in statements if s != statement), None)
#             false_branch_statement = next((s for s in statements if s != statement and s != true_branch_statement), None)

#             true_branch_node = f"N{node_counter}"
#             false_branch_node = f"N{node_counter + 1}"
#             node_counter += 2

#             if true_branch_statement:
#                 control_flow_graph[true_branch_node] = {"type": analyze_statement(true_branch_statement), "content": true_branch_statement, "next": []}
#             else:
#                 control_flow_graph[true_branch_node] = {"type": "process", "content": "True Branch", "next": []}

#             if false_branch_statement:
#                 control_flow_graph[false_branch_node] = {"type": analyze_statement(false_branch_statement), "content": false_branch_statement, "next": []}
#             else:
#                 control_flow_graph[false_branch_node] = {"type": "process", "content": "False Branch", "next": []}

#             control_flow_graph[new_node]["next"] = [true_branch_node, false_branch_node]
#             control_flow_graph[current_node]["next"].append(new_node)

#             current_node = true_branch_node
#         else:
#             control_flow_graph[current_node]["next"].append(new_node)
#             current_node = new_node

#     control_flow_graph["End"] = {"type": "end", "content": "End Node", "next": []}

#     for node, data in control_flow_graph.items():
#         if len(data["next"]) == 0 and data["type"] != "end":
#             data["next"].append("End")

#     return control_flow_graph

# -----------------------------------------------------------------------------------------

def remove_duplicate_nodes(cfg):
    seen_nodes = {}  # Dictionary to store unique nodes
    nodes_to_remove = []  # List to track duplicate nodes

    # First pass: Identify and mark duplicate nodes
    for node, data in cfg.items():
        node_content = data['content']
        if node_content in seen_nodes:
            original_node = seen_nodes[node_content]
            nodes_to_remove.append(node)

            # Update all references in 'next' to point to the original node
            for n, d in cfg.items():
                d['next'] = [original_node if x == node else x for x in d['next']]
        else:
            seen_nodes[node_content] = node

    # Second pass: Remove the duplicate nodes
    for node in nodes_to_remove:
        del cfg[node]

    return cfg

def acfd(use_case_data):
    statements = extract_statements(use_case_data)
    control_flow_graph = {"Root": {"type": "start", "content": "Root Node", "next": []}}
    current_node = "Root"
    node_counter = 1

    for idx, statement in enumerate(statements):
        statement_type = analyze_statement(statement)
        new_node = f"N{node_counter}"
        control_flow_graph[new_node] = {"type": statement_type, "content": statement, "next": []}
        node_counter += 1

        if statement_type == "condition":
            true_branch_statement = statements[idx + 1] if idx + 1 < len(statements) else "True Branch"
            false_branch_statement = statements[idx + 2] if idx + 2 < len(statements) else "False Branch"

            true_branch_node = f"N{node_counter}"
            false_branch_node = f"N{node_counter + 1}"
            node_counter += 2

            control_flow_graph[true_branch_node] = {"type": analyze_statement(true_branch_statement), "content": true_branch_statement, "next": []}
            control_flow_graph[false_branch_node] = {"type": analyze_statement(false_branch_statement), "content": false_branch_statement, "next": []}

            control_flow_graph[new_node]["next"] = [true_branch_node, false_branch_node]
            control_flow_graph[current_node]["next"].append(new_node)

            current_node = true_branch_node
        else:
            control_flow_graph[current_node]["next"].append(new_node)
            current_node = new_node

    control_flow_graph["End"] = {"type": "end", "content": "End Node", "next": []}

    for node, data in control_flow_graph.items():
        if len(data["next"]) == 0 and data["type"] != "end":
            data["next"].append("End")

    # Remove duplicate nodes
    control_flow_graph = remove_duplicate_nodes(control_flow_graph)

    return control_flow_graph


def generate_test_paths(control_flow_graph):
    def dfs(current_node, path, all_paths):
        if current_node == "End":
            all_paths.append(path.copy())
            return
        for next_node in control_flow_graph[current_node]["next"]:
            path.append(next_node)
            dfs(next_node, path, all_paths)
            path.pop()

    all_paths = []
    dfs("Root", ["Root"], all_paths)
    return all_paths

def visualize_control_flow_graph(control_flow_graph, test_case=None, test_case_index=None):
    dot = Digraph(comment=f'Control Flow Diagram - Test Case {test_case_index}' if test_case_index else 'Control Flow Diagram')
    dot.attr(rankdir='TB')
    for node, data in control_flow_graph.items():
        node_label = f"{node}\n({data['type']})\n{data['content']}"
        if test_case and node in test_case:
            dot.node(node, label=node_label, color='lightblue2', style='filled')
        else:
            dot.node(node, label=node_label)

    for node, data in control_flow_graph.items():
        for next_node in data.get("next", []):
            dot.edge(node, next_node)

    filename = f'control_flow_graph_test_case_{test_case_index}' if test_case_index else 'control_flow_graph'
    dot.render(filename, view=True, format='pdf')
