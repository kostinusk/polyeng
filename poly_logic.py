import copy
import random
import time

class Unit:
    def __init__(self, player, x, y, strength=1):
        self.player = player
        self.x = x
        self.y = y
        self.strength = strength

class City:
    def __init__(self, player, x, y, population=1):
        self.player = player
        self.x = x
        self.y = y
        self.population = population

class GameState:
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height
        self.units = []
        self.cities = []
        self.technologies = {0: set(), 1: set()}
        self.current_player = 0
        self.visibility = {0: set(), 1: set()}
        self.update_visibility()

    def update_visibility(self):
        for p in [0, 1]:
            self.visibility[p] = set()
            for unit in self.units:
                if unit.player == p:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = unit.x + dx, unit.y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                self.visibility[p].add((nx, ny))

    def is_visible(self, player, x, y):
        return (x, y) in self.visibility[player]

    def generate_moves(self):
        moves = []
        for unit in self.units:
            if unit.player == self.current_player:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = unit.x + dx, unit.y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        target = self.get_unit_at(nx, ny)
                        if target and target.player != unit.player:
                            moves.append(('attack', unit, target))
                        else:
                            moves.append(('move', unit, nx, ny))
                if 'build' in self.technologies[self.current_player]:
                    if not self.get_city_at(unit.x, unit.y):
                        moves.append(('build_city', unit))
        if random.random() < 0.3:
            new_tech = random.choice(['build', 'sailing'])
            if new_tech not in self.technologies[self.current_player]:
                moves.append(('research', new_tech))
        return moves

    def apply_move(self, move):
        new_state = copy.deepcopy(self)
        action = move[0]

        if action == 'move':
            _, unit, x, y = move
            for u in new_state.units:
                if u.x == unit.x and u.y == unit.y and u.player == unit.player:
                    u.x, u.y = x, y

        elif action == 'attack':
            _, attacker, target = move
            new_state.units = [u for u in new_state.units if not (u.x == target.x and u.y == target.y and u.player == target.player)]
            for u in new_state.units:
                if u.x == attacker.x and u.y == attacker.y and u.player == attacker.player:
                    u.strength += 1

        elif action == 'build_city':
            _, unit = move
            new_state.cities.append(City(unit.player, unit.x, unit.y))

        elif action == 'research':
            _, tech = move
            new_state.technologies[new_state.current_player].add(tech)

        new_state.current_player = 1 - self.current_player
        new_state.update_visibility()
        return new_state

    def get_unit_at(self, x, y):
        for unit in self.units:
            if unit.x == x and unit.y == y:
                return unit
        return None

    def get_city_at(self, x, y):
        for city in self.cities:
            if city.x == x and city.y == y:
                return city
        return None

    def evaluate(self):
        score = 0
        for city in self.cities:
            score += (1 if city.player == self.current_player else -1) * city.population
        for unit in self.units:
            score += (1 if unit.player == self.current_player else -1) * unit.strength
        score += len(self.technologies[self.current_player]) * 2
        return score

    def render(self):
        grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
        for city in self.cities:
            grid[city.y][city.x] = 'C' + str(city.player)
        for unit in self.units:
            grid[unit.y][unit.x] = 'U' + str(unit.player)
        print("\nCurrent map (P{}'s turn):".format(self.current_player))
        for row in grid:
            print(' '.join(row))
        print("-------------------------")

def minimax(state, depth, maximizing_player):
    if depth == 0:
        return state.evaluate(), None

    moves = state.generate_moves()
    if not moves:
        return state.evaluate(), None

    best_value = float('-inf') if maximizing_player else float('inf')
    best_move = None

    for move in moves:
        new_state = state.apply_move(move)
        val, _ = minimax(new_state, depth - 1, not maximizing_player)
        if maximizing_player and val > best_value:
            best_value, best_move = val, move
        elif not maximizing_player and val < best_value:
            best_value, best_move = val, move

    return best_value, best_move

if __name__ == "__main__":
    state = GameState()
    state.units = [Unit(0, 1, 1), Unit(1, 3, 3)]
    state.cities = [City(0, 0, 0), City(1, 4, 4)]

    for _ in range(10):
        state.render()
        score, best_move = minimax(state, depth=2, maximizing_player=True)
        if best_move is None:
            print("No valid moves for player", state.current_player)
            break
        state = state.apply_move(best_move)
        time.sleep(0.5)

