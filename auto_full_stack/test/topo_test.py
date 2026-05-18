#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/6 21:52
@Author  : Rex
@File    : topo_test.py
"""
import json

class IncrementNode:
    def __init__(self, data):
        self.id = data["id"]
        self.data = data
        self.dependencies = data.get("dependencies", [])
        self.children = []

    def __repr__(self):
        return f"Node({self.id}, name='{self.data.get('name')}')"

def __build_dependency_graph(increments):
    """
    Build incremental dependency graph
    """
    nodes = {item["id"]: IncrementNode(item) for item in increments}
    for node in nodes.values():
        for dep_id in node.dependencies:
            if dep_id in nodes:
                nodes[dep_id].children.append(node)
    return nodes

def __topological_sort(nodes):
    """
    Topological sort using Kahn's algorithm
    """
    indegree = {node_id: 0 for node_id in nodes}
    for node in nodes.values():
        for child in node.children:
            indegree[child.id] += 1

    queue = [nodes[nid] for nid, deg in indegree.items() if deg == 0]
    sorted_nodes = []

    while queue:
        current = queue.pop(0)
        sorted_nodes.append(current.data)
        for child in current.children:
            indegree[child.id] -= 1
            if indegree[child.id] == 0:
                queue.append(child)
    return sorted_nodes

def __print_dependency_graph(nodes):
    """
    Print the incremental dependency graph
    """
    print("=== Topological Dependency Graph ===")
    for node in nodes.values():
        if node.children:
            children_names = ", ".join(
                [f"{child.id}:{child.data['name']}" for child in node.children]
            )
            print(f"{node.id}:{node.data['name']}  →  {children_names}")
        else:
            print(f"{node.id}:{node.data['name']}  →  (NULL)")


if __name__ == "__main__":
    increment_list = [
        {
            "id": 1,
            "name": "Basic Framework Setup",
            "description": "Set up the initial project structure, including user authentication and database connection.",
            "dependencies": [],
            "priority": "high"
        },
        {
            "id": 2,
            "name": "Student Management",
            "description": "Implement student info CRUD operations: add, update, delete, and view student records. Include search functionality using criteria such as name, ID, or major.",
            "dependencies": [
                1
            ],
            "priority": "high",
            "module_name": "Student"
        },
        {
            "id": 3,
            "name": "Course Management",
            "description": "Implement course info CRUD operations: create, modify, and delete course records. Include functionality to manage course enrollment details.",
            "dependencies": [
                1
            ],
            "priority": "medium",
            "module_name": "Course"
        },
        {
            "id": 4,
            "name": "Grade Management",
            "description": "Implement grade input, update, and retrieval functionalities. Include functionality to generate grade reports for students or entire classes.",
            "dependencies": [
                1,
                2,
                3
            ],
            "priority": "medium",
            "module_name": "Grade"
        }
    ]
    print(json.dumps(increment_list, indent=4))
    graph = __build_dependency_graph(increments=increment_list)

    __topological_sort(graph)

    __print_dependency_graph(graph)
