import sys
import time
import math
from collections import deque
from heapq import heappop, heappush

MAX_VALUE = 10**9

class Node:
 
    def __init__(self, value, parent=None, operation=None, cost_g=0, cost_h=0):
        self.value = value       
        self.parent = parent      
        self.operation = operation
        self.cost_g = cost_g     
        self.cost_h = cost_h     

    def __lt__(self, other):

        return (self.cost_g + self.cost_h) < (other.cost_g + other.cost_h)

    def __eq__(self, other):
        return isinstance(other, Node) and self.value == other.value

    def __hash__(self):
        return hash(self.value)


def admissible_heuristic(current_value, target_value):
   
    diff = abs(target_value - current_value)
    return diff // 2

def get_successor_nodes(current_node, target_value):
 
    X = current_node.value
    successors = []

    def add_op(name, new_X, op_cost):
        new_g = current_node.cost_g + op_cost
        new_h = admissible_heuristic(new_X, target_value)
        successors.append(Node(new_X, current_node, (name, X, op_cost), new_g, new_h))

    if X < MAX_VALUE:
        add_op('increase', X + 1, 2)

    if X > 0:
        add_op('decrease', X - 1, 2)

    if X > 0 and 2 * X <= MAX_VALUE:
        op_cost = math.ceil(X / 2) + 1
        add_op('double', 2 * X, op_cost)

    if X > 0:
        op_cost = math.ceil(X / 4) + 1
        add_op('half', X // 2, op_cost)

    if X**2 <= MAX_VALUE:
        op_cost = math.ceil(X / 4) + 1
        add_op('square', X**2, op_cost)

    if X > 1:
        root_X = math.isqrt(X)
        if root_X * root_X == X: 
            op_cost = math.ceil((X - root_X) / 4) + 1
            add_op('root', root_X, op_cost)

    return successors




def find_path(start_value, target_value, search_method):

    start_time = time.time()
    initial_node = Node(start_value, cost_h=admissible_heuristic(start_value, target_value))
    
    visited = {start_value}
    nodes_expanded = 0

    if search_method == 'breadth':
        queue = deque([initial_node])

        while queue:
            current_node = queue.popleft()
            nodes_expanded += 1

            if current_node.value == target_value:
                return current_node, nodes_expanded, time.time() - start_time

            for successor in get_successor_nodes(current_node, target_value):
                if successor.value not in visited:
                    visited.add(successor.value)
                    queue.append(successor)

    elif search_method == 'depth':
        stack = [initial_node]

        while stack:
            current_node = stack.pop()
            nodes_expanded += 1
            
            if current_node.value == target_value:
                return current_node, nodes_expanded, time.time() - start_time
            
            if current_node.value in visited and current_node.value != start_value:
                 continue
            visited.add(current_node.value)

            for successor in reversed(get_successor_nodes(current_node, target_value)):
                if successor.value not in visited:
                    stack.append(successor)

    elif search_method in ['best', 'astar']:
        priority_queue = [initial_node]
        best_g = {start_value: 0} 
        
        while priority_queue:
            current_node = heappop(priority_queue)
            
            if current_node.value == target_value:
                return current_node, nodes_expanded, time.time() - start_time
            
            if current_node.cost_g > best_g.get(current_node.value, float('inf')):
                continue

            nodes_expanded += 1

            for successor in get_successor_nodes(current_node, target_value):
                if search_method == 'best':
                    successor.cost_g = 0 # f(n) = h(n)

                if successor.cost_g < best_g.get(successor.value, float('inf')):
                    best_g[successor.value] = successor.cost_g
                    heappush(priority_queue, successor)

    else:
        print(f"Σφάλμα: Άγνωστη μέθοδος αναζήτησης '{search_method}'. Επιτρέπονται: breadth, depth, best, astar.", file=sys.stderr)
        return None, 0, 0
    
    return None, nodes_expanded, time.time() - start_time



def reconstruct_path(goal_node):
  
    path = []
    current = goal_node
    while current.parent:
        op_name, op_number, op_cost = current.operation
        path.append((op_name, op_number, op_cost))
        current = current.parent
    
    path.reverse()
    total_cost = goal_node.cost_g
    return path, total_cost

def write_solution_to_file(path, total_cost, file_name):
  
    try:
        N = len(path)
        with open(file_name, 'w') as f:
            f.write(f"{N}, {total_cost}\n")
            
            for op_name, op_number, op_cost in path:
                f.write(f"{op_name} {op_number} {op_cost}\n")
        
        print(f"Η λύση γράφτηκε με επιτυχία στο αρχείο '{file_name}'.")

    except Exception as e:
        print(f"Σφάλμα κατά τη γραφή στο αρχείο: {e}", file=sys.stderr)




def main():
    if len(sys.argv) != 5:
        print("Σφάλμα: Λάθος αριθμός ορισμάτων.", file=sys.stderr)
        print("Χρήση: python register.py <method> <start_val> <target_val> <output_file>", file=sys.stderr)
        print("Παράδειγμα: python register.py breadth 5 18 solution.txt", file=sys.stderr)
        sys.exit(1)

    search_method = sys.argv[1].lower()
    
    try:
        start_value = int(sys.argv[2])
        target_value = int(sys.argv[3])
        output_file = sys.argv[4]
    except ValueError:
        print("Σφάλμα: Οι τιμές αρχής και στόχου πρέπει να είναι ακέραιοι.", file=sys.stderr)
        sys.exit(1)

    print(f"Εκτέλεση Αναζήτησης ({search_method.upper()}) για {start_value} -> {target_value}...")
    
    solution_node, expanded_count, elapsed_time = find_path(start_value, target_value, search_method)

    print("-" * 30)
    print(f"Στατιστικά:")
    print(f"Χρόνος Εκτέλεσης: {elapsed_time:.4f} δευτερόλεπτα")
    print(f"Κόμβοι που εξετάστηκαν: {expanded_count}")

    if solution_node:
        path, total_cost = reconstruct_path(solution_node)
        
        print(f"Λύση Βρέθηκε!")
        print(f"Μήκος Λύσης (Βήματα): {len(path)}")
        print(f"Συνολικό Κόστος: {total_cost}")
        
        write_solution_to_file(path, total_cost, output_file)
    else:
        print("Αδυναμία επίλυσης του προβλήματος.")

if __name__ == '__main__':
    main()