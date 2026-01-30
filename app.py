import streamlit as st
import numpy as np
import random
from datetime import date

# --- 설정 및 상수 ---
BOARD_SIZE = 15
EMPTY, PLAYER, AI = 0, 1, 2

# --- 게임 로직 클래스 ---
class GomokuGame:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    def reset_game(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    def make_move(self, r, c, player):
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r, c] == EMPTY:
            self.board[r, c] = player
            return True
        return False
    def check_win(self, player):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == player:
                    for dr, dc in [(0,1), (1,0), (1,1), (1,-1)]:
                        count = 0
                        for i in range(5):
                            nr, nc = r + dr*i, c + dc*i
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr, nc] == player:
                                count += 1
                            else: break
                        if count == 5: return True
        return False

# --- UI 세션 초기화 ---
st.set_page_config(page_title="고수 AI 오목", layout="centered")

if 'game' not in st.session_state:
    st.session_state.game = GomokuGame()
    st.session_state.board = st.session_state.game.board
    st.session_state.game_over = False
    st.session_state.current_player = PLAYER

# --- 메인 화면 ---
st.title("⚫ 고수 AI 오목 대결 ⚪")

if st.button("게임 리셋"):
    st.session_state.game.reset_game()
    st.session_state.board = st.session_state.game.board
    st.session_state.game_over = False
    st.session_state.current_player = PLAYER
    st.rerun()

# 보드 출력 및 클릭 처리
for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        val = st.session_state.board[r, c]
        lbl = "⚫" if val == PLAYER else ("⚪" if val == AI else " ")
        if cols[c].button(lbl, key=f"{r}_{c}", disabled=st.session_state.game_over or val != EMPTY):
            # 플레이어 이동
            if st.session_state.game.make_move(r, c, PLAYER):
                if st.session_state.game.check_win(PLAYER):
                    st.session_state.game_over = True
                    st.success("당신이 승리했습니다!")
                else:
                    # 간단한 AI 이동 (빈칸 중 랜덤)
                    empty_cells = np.argwhere(st.session_state.board == EMPTY)
                    if len(empty_cells) > 0:
                        ar, ac = random.choice(empty_cells)
                        st.session_state.game.make_move(ar, ac, AI)
                        if st.session_state.game.check_win(AI):
                            st.session_state.game_over = True
                            st.error("AI가 승리했습니다!")
                st.rerun()

st.markdown("<style>button {width:30px !important; height:30px !important; padding:0 !important;}</style>", unsafe_allow_html=True)
