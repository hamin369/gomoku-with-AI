import numpy as np
import random

BOARD_SIZE = 15
EMPTY = 0
PLAYER = 1
AI = 2

class GomokuGame:
    def __init__(self, difficulty="easy"):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = PLAYER # 1: 사용자, 2: AI
        self.difficulty = difficulty

    def reset_game(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = PLAYER
        return self.board

    def is_valid_move(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r, c] == EMPTY

    def make_move(self, r, c, player):
        if self.is_valid_move(r, c):
            self.board[r, c] = player
            return True
        return False

    def check_win(self, player):
        # 가로, 세로, 대각선 승리 판정
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == player:
                    # 가로
                    if c + 4 < BOARD_SIZE and np.all(self.board[r, c:c+5] == player):
                        return True
                    # 세로
                    if r + 4 < BOARD_SIZE and np.all(self.board[r:r+5, c] == player):
                        return True
                    # 우하향 대각선
                    if r + 4 < BOARD_SIZE and c + 4 < BOARD_SIZE and \
                       np.all([self.board[r+i, c+i] == player for i in range(5)]):
                        return True
                    # 좌하향 대각선
                    if r + 4 < BOARD_SIZE and c - 4 >= 0 and \
                       np.all([self.board[r+i, c-i] == player for i in range(5)]):
                        return True
        return False

    def is_board_full(self):
        return np.all(self.board != EMPTY)

    def get_empty_cells(self):
        empty_cells = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    empty_cells.append((r, c))
        return empty_cells

    def ai_move(self):
        if self.difficulty == "easy":
            return self._ai_easy()
        elif self.difficulty == "medium":
            return self._ai_medium()
        elif self.difficulty == "hard":
            return self._ai_hard()
        return self._ai_easy() # 기본값

    def _ai_easy(self):
        # 무작위로 비어있는 곳에 둡니다.
        empty_cells = self.get_empty_cells()
        if empty_cells:
            return random.choice(empty_cells)
        return None

    def _ai_medium(self):
        # 1. 자신의 승리 경로 확인 (이기기)
        for r, c in self.get_empty_cells():
            self.board[r, c] = AI
            if self.check_win(AI):
                return r, c
            self.board[r, c] = EMPTY

        # 2. 플레이어의 승리 경로 확인 (막기)
        for r, c in self.get_empty_cells():
            self.board[r, c] = PLAYER
            if self.check_win(PLAYER):
                self.board[r, c] = EMPTY
                return r, c
            self.board[r, c] = EMPTY

        # 3. 무작위로 두기 (기본 전략)
        return self._ai_easy()

    def _ai_hard(self):
        # 1. 자신의 승리 경로 확인 (이기기)
        for r, c in self.get_empty_cells():
            self.board[r, c] = AI
            if self.check_win(AI):
                return r, c
            self.board[r, c] = EMPTY

        # 2. 플레이어의 승리 경로 확인 (막기)
        for r, c in self.get_empty_cells():
            self.board[r, c] = PLAYER
            if self.check_win(PLAYER):
                self.board[r, c] = EMPTY
                return r, c
            self.board[r, c] = EMPTY

        # 3. 중앙에 가까운 곳에 두기
        center_r, center_c = BOARD_SIZE // 2, BOARD_SIZE // 2
        
        # 중앙 우선순위
        empty_cells = self.get_empty_cells()
        
        # 중앙에서 가까운 순서로 정렬
        empty_cells.sort(key=lambda cell: (cell[0] - center_r)**2 + (cell[1] - center_c)**2)

        for r, c in empty_cells:
            # 4. 3x3 또는 4x4 형태를 만드는 시도 (매우 기본적인 휴리스틱)
            # 이 부분은 Minimax나 더 복잡한 알고리즘으로 대체될 수 있습니다.
            # 여기서는 단순히 근처에 돌이 있으면 우선시하는 정도로 구현합니다.
            
            # 주변 8칸에 돌이 있는지 확인
            has_neighbor = False
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr, nc] != EMPTY:
                        has_neighbor = True
                        break
                if has_neighbor:
                    break
            
            if has_neighbor:
                return r,c
            
        # 모든 전략이 실패하면 무작위
        return self._ai_easy()