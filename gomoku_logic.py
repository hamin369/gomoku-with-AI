import numpy as np
import random

BOARD_SIZE = 15
EMPTY = 0
PLAYER = 1
AI = 2

class GomokuGame:
    def __init__(self, difficulty="easy"):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.difficulty = difficulty

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
        # 1. 모든 난이도 공통: 내가 지금 바로 이길 자리가 있다면 무조건 둡니다.
        winning_move = self._find_immediate_win(AI)
        if winning_move:
            return winning_move

        # 2. 난이도별 로직 분기
        if self.difficulty == "easy":
            # [쉬움] 상대방의 승리 기회를 30% 확률로만 막습니다. 나머지는 무작위.
            if random.random() < 0.3:
                threat = self._find_immediate_win(PLAYER)
                if threat: return threat
            return self._get_random_move()

        elif self.difficulty == "medium":
            # [중간] 상대방의 승리 기회는 100% 막지만, 공격적인 수읽기는 약합니다.
            threat = self._find_immediate_win(PLAYER)
            if threat: return threat
            return self._get_best_move(defense_weight=0.8)

        else: # hard
            # [어려움] 상대방의 승리 기회를 막는 것은 물론, 3-3 등을 방어하기 위해 수비 가중치를 높입니다.
            threat = self._find_immediate_win(PLAYER)
            if threat: return threat
            return self._get_best_move(defense_weight=1.5)

    def _find_immediate_win(self, player):
        """한 수만 두면 바로 이기는 자리가 있는지 확인"""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    self.board[r, c] = player
                    if self.check_win(player):
                        self.board[r, c] = EMPTY
                        return (r, c)
                    self.board[r, c] = EMPTY
        return None

    def _get_random_move(self):
        empty_cells = np.argwhere(self.board == EMPTY)
        if len(empty_cells) > 0:
            idx = random.randint(0, len(empty_cells) - 1)
            return tuple(empty_cells[idx])
        return None

    def _get_best_move(self, defense_weight):
        best_score = -1
        best_moves = []
        
        # 보드 전체를 탐색하며 점수 계산
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    # 주변에 돌이 있는 칸 위주로 계산 (성능 최적화)
                    if not self._has_neighbor(r, c):
                        continue
                        
                    score = self._evaluate_position(r, c, defense_weight)
                    if score > best_score:
                        best_score = score
                        best_moves = [(r, c)]
                    elif score == best_score:
                        best_moves.append((r, c))
        
        if not best_moves:
            return (BOARD_SIZE // 2, BOARD_SIZE // 2) if self.board[7,7] == EMPTY else self._get_random_move()
            
        return random.choice(best_moves)

    def _has_neighbor(self, r, c):
        """해당 칸 주변 2칸 이내에 돌이 있는지 확인 (탐색 효율성)"""
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr, nc] != EMPTY:
                    return True
        return False

    def _evaluate_position(self, r, c, defense_weight):
        # AI의 공격 점수와 사용자의 방어 점수를 합산
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
                else:
                    line.append(-1)
            
            total_score += self._calculate_pattern_score(line, player)
        return total_score

    def _calculate_pattern_score(self, line, player):
        # 돌의 개수와 열린 공간에 따른 점수 산정
        line_str = "".join([str(x) if x == player else ("E" if x == EMPTY else "X") for x in line])
        
        # 4개 연속 (열린 4목)
        if "E1111E".replace("1", str(player)) in line_str: return 10000
        # 4개 연속 (막힌 4목)
        if "1111E".replace("1", str(player)) in line_str or "E1111".replace("1", str(player)) in line_str: return 5000
        # 3개 연속 (열린 3목)
        if "E111E".replace("1", str(player)) in line_str: return 1000
        # 2개 연속 (열린 2목)
        if "E11E".replace("1", str(player)) in line_str: return 100
        
        return 0
