class Node:
    """Represents a single concept token."""
    def __init__(self, token: str):
        self.token = token


class Matrix:
    """Adjacency matrix referencing Nodes."""
    def __init__(self, name: str):
        self.name = name
        # adjacency[token_a][token_b] = weight
        self.adjacency = {}

    def add_node(self, node: Node):
        self.adjacency.setdefault(node.token, {})

    def add_edge(self, node_a: Node, node_b: Node, weight: float = 1.0):
        self.add_node(node_a)
        self.add_node(node_b)
        self.adjacency[node_a.token][node_b.token] = weight
        self.adjacency[node_b.token][node_a.token] = weight

    def neighbors(self, token: str):
        return self.adjacency.get(token, {})


class SuperKnowledgeGraph:
    """Hierarchical structure of overlapping matrices."""
    def __init__(self):
        self.nodes = {}
        self.matrices = {}

    def get_node(self, token: str) -> Node:
        if token not in self.nodes:
            self.nodes[token] = Node(token)
        return self.nodes[token]

    def get_matrix(self, name: str) -> Matrix:
        if name not in self.matrices:
            self.matrices[name] = Matrix(name)
        return self.matrices[name]

    def connect(self, matrix_name: str, token_a: str, token_b: str, weight: float = 1.0):
        node_a = self.get_node(token_a)
        node_b = self.get_node(token_b)
        matrix = self.get_matrix(matrix_name)
        matrix.add_edge(node_a, node_b, weight)

    def matrices_for_token(self, token: str):
        return [name for name, mat in self.matrices.items() if token in mat.adjacency]

    def traverse(self, start_token: str, max_steps: int = 5):
        visited = set()
        queue = [(start_token, m) for m in self.matrices_for_token(start_token)]
        path = []
        steps = 0
        while queue and steps < max_steps:
            token, matrix_name = queue.pop(0)
            if (token, matrix_name) in visited:
                continue
            visited.add((token, matrix_name))
            path.append({"matrix": matrix_name, "token": token})
            neighbors = self.matrices[matrix_name].neighbors(token)
            for n in neighbors:
                for m in self.matrices_for_token(n):
                    if (n, m) not in visited:
                        queue.append((n, m))
            steps += 1
        return path
