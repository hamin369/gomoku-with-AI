def ai_move(self):
        # 1. 공통: 내가 지금 바로 이길 수 있는 수(5목)가 있다면 무조건 둡니다.
        # (이걸 안 하면 아무리 쉬움이라도 바보처럼 보입니다.)
        winning_move = self._find_immediate_win(AI)
        if winning_move: return winning_move

        # 2. 난이도별 로직
        if self.difficulty == "easy":
            # 상대방의 4목을 50% 확률로만 막습니다. (가끔 실수함)
            if random.random() < 0.5:
                threat = self._find_immediate_win(PLAYER)
                if threat: return threat
            return self._get_random_move()

        elif self.difficulty == "medium":
            # 상대방의 당장 끝나는 수(4목)는 100% 막지만, 
            # 3목을 만들거나 멀리 내다보는 수읽기는 부족하게 설정합니다.
            threat = self._find_immediate_win(PLAYER)
            if threat: return threat
            return self._get_best_move(defense_weight=0.7) # 하드보다 방어력이 낮음

        else: # hard
            return self._get_best_move(defense_weight=1.2)

    def _find_immediate_win(self, player):
        """당장 이길 수 있는 자리가 있는지 찾는 함수"""
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
        """점수 기반 최적의 수 찾기"""
        best_score = -1
        best_moves = []
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == EMPTY:
                    score = self._evaluate_position(r, c, defense_weight)
                    if score > best_score:
                        best_score = score
                        best_moves = [(r, c)]
                    elif score == best_score:
                        best_moves.append((r, c))
        
        return random.choice(best_moves) if best_moves else self._get_random_move()

    def _evaluate_position(self, r, c, defense_weight):
        attack_score = self._get_score_for_player(r, c, AI)
        defense_score = self._get_score_for_player(r, c, PLAYER)
        return attack_score + (defense_score * defense_weight)
