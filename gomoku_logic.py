import numpy as np
import random

BOARD_SIZE = 15
EMPTY = 0
PLAYER = 1
AI = 2

class GomokuGame:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

    def reset_game(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        return self.board

    def make_move(self, r, c, player):
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r, c] == EMPTY:
            self.board[r, c] = player
            return True
        return False

    def check_win(self, player):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == player:
                    if self._check_direction(r, c, 0, 1, player) or \
                       self._check_direction(r, c, 1, 0, player) or \
                       self._check_direction(r, c, 1, 1, player) or \
                       self._check_direction(r, c, 1, -1, player):
                        return True
        return False

    def _check_direction(self, r, c, dr, dc, player):
        count = 0
        for i in range(5):
            nr, nc = r + dr*i, c + dc*i
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr, nc] == player:
                count += 1
            else: break
        return count == 5

    def is_board_full(self):
        return not np.any(self.board == EMPTY)

    def ai_move(self):
        # 1. 즉시 승리할 자리가 있는지 확인
        winning_move = self._find_immediate_win(AI)
        if winning_move: return winning_move

        # 2. 상대방(플레이어)이 즉시 승리할 자리가 있다면 무조건 방어
        threat = self._find_immediate_win(PLAYER)
        if threat: return threat

        # 3. 최적의 수 계산 (수비 가중치 1.5로 고정)
        return self._get_best_move(defense_weight=1.5)

    def _find_immediate_win(self, player):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    self.board[r, c] = player
                    if self.check_win(player):
                        self.board[r, c] = EMPTY
                        return (r, c)
                    self.board[r, c] = EMPTY
        return None

    def _get_best_move(self, defense_weight):
        best_score = -1
        best_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    if not self._has_neighbor(r, c): continue
                    score = self._evaluate_position(r, c, defense_weight)
                    if score > best_score:
                        best_score = score
                        best_moves = [(r, c)]
                    elif score == best_score:
                        best_moves.append((r, c))
        
        if not best_moves:
            return (7, 7) if self.board[7,7] == EMPTY else self._get_random_move()
        return random.choice(best_moves)

    def _has_neighbor(self, r, c):
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr, nc] != EMPTY:
                    return True
        return False

    def _evaluate_position(self, r, c, defense_weight):
        attack_score = self._get_score_for_player(r, c, AI)
        defense_score = self._get_score_for_player(r, c, PLAYER)
        return attack_score + (defense_score * defense_weight)

    def _get_score_for_player(self, r, c, player):
        total_score = 0
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            line = []
            for i in range(-4, 5):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    line.append(self.board[nr, nc])
                else: line.append(-1)
            total_score += self._calculate_pattern_score(line, player)
        return total_score

    def _calculate_pattern_score(self, line, player):
        line_str = "".join([str(x) if x == player else ("E" if x == EMPTY else "X") for x in line])
        if "E1111E".replace("1", str(player)) in line_str: return 10000
        if "1111E".replace("1", str(player)) in line_str or "E1111".replace("1", str(player)) in line_str: return 5000
        if "E111E".replace("1", str(player)) in line_str: return 1000
        if "E11E".replace("1", str(player)) in line_str: return 100
        return 0

    def _get_random_move(self):
        empty_cells = np.argwhere(self.board == EMPTY)
        if len(empty_cells) > 0:
            idx = random.randint(0, len(empty_cells) - 1)
            return tuple(empty_cells[idx])
        return None
