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
        # 1. 공격: 당장 내가 이길 수 있는 곳(5목) 찾기
        win = self._find_immediate_win(AI)
        if win: return win

        # 2. 수비: 상대방이 당장 이길 곳(4목) 막기
        defend = self._find_immediate_win(PLAYER)
        if defend: return defend

        # 3. 전략적 공격/수비: 점수 시스템 가동
        return self._get_best_move()

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

    def _get_best_move(self):
        best_score = -1
        best_moves = []
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    if not self._has_neighbor(r, c): continue
                    
                    # AI 점수와 플레이어 점수를 별도로 계산
                    # 공격 가중치와 수비 가중치를 전략적으로 배분
                    a_score = self._get_score_for_player(r, c, AI)
                    p_score = self._get_score_for_player(r, c, PLAYER)
                    
                    # 플레이어의 열린 3목이나 4목은 매우 높은 점수로 수비
                    # AI 본인의 공격 기회도 강력하게 평가
                    total_score = a_score + (p_score * 1.4) 
                    
                    if total_score > best_score:
                        best_score = total_score
                        best_moves = [(r, c)]
                    elif total_score == best_score:
                        best_moves.append((r, c))
        
        if not best_moves:
            return (7, 7) if self.board[7,7] == EMPTY else self._get_random_move()
        return random.choice(best_moves)

    def _has_neighbor(self, r, c):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr, nc] != EMPTY:
                    return True
        return False

    def _get_score_for_player(self, r, c, player):
        total = 0
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            line = []
            for i in range(-4, 5):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    line.append(self.board[nr, nc])
                else: line.append(-1)
            total += self._pattern_analysis(line, player)
        return total

    def _pattern_analysis(self, line, player):
        S = "".join([str(x) if x == player else ("E" if x == EMPTY else "X") for x in line])
        # 고득점 패턴 (점수 설계)
        if "11111".replace("1", str(player)) in S: return 50000     # 5목
        if "E1111E".replace("1", str(player)) in S: return 10000    # 열린 4목
        if "E111E".replace("1", str(player)) in S: return 3000      # 열린 3목
        if "E111X".replace("1", str(player)) in S or "X111E".replace("1", str(player)) in S: return 1000 # 막힌 4목
        if "E11E".replace("1", str(player)) in S: return 500       # 열린 2목
        if "E1E1E".replace("1", str(player)) in S: return 400      # 띄엄 3목
        return 0

    def _get_random_move(self):
        empty_cells = np.argwhere(self.board == EMPTY)
        if len(empty_cells) > 0:
            idx = random.randint(0, len(empty_cells) - 1)
            return tuple(empty_cells[idx])
        return None
