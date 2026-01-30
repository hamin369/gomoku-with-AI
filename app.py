import streamlit as st
from gomoku_logic import GomokuGame, PLAYER, AI, EMPTY, BOARD_SIZE

st.set_page_config(page_title="고수 AI 오목", page_icon="⚫", layout="centered")

if 'game' not in st.session_state:
    st.session_state.game = GomokuGame()
if 'board' not in st.session_state:
    st.session_state.board = st.session_state.game.board.copy()
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'current_player' not in st.session_state:
    st.session_state.current_player = PLAYER
if 'message' not in st.session_state:
    st.session_state.message = "당신은 흑돌(⚫)입니다. 비어있는 칸을 클릭하세요!"

st.title("⚫ 고수 AI와 한판 승부 ⚪")

if st.sidebar.button("게임 다시 시작"):
    st.session_state.game.reset_game()
    st.session_state.board = st.session_state.game.board.copy()
    st.session_state.game_over = False
    st.session_state.current_player = PLAYER
    st.session_state.message = "새 게임이 시작되었습니다!"
    st.rerun()

def play_step(r, c):
    if st.session_state.game_over or st.session_state.board[r, c] != EMPTY:
        return
    if st.session_state.game.make_move(r, c, PLAYER):
        st.session_state.board = st.session_state.game.board.copy()
        if st.session_state.game.check_win(PLAYER):
            st.session_state.game_over = True
            st.session_state.message = "🎉 승리했습니다! 정말 대단하시네요!"
        elif st.session_state.game.is_board_full():
            st.session_state.game_over = True
            st.session_state.message = "무승부입니다!"
        else:
            st.session_state.current_player = AI
            st.rerun()

if not st.session_state.game_over and st.session_state.current_player == AI:
    with st.spinner("AI가 수읽기 중..."):
        ai_move = st.session_state.game.ai_move()
        if ai_move:
            r, c = ai_move
            st.session_state.game.make_move(r, c, AI)
            st.session_state.board = st.session_state.game.board.copy()
            if st.session_state.game.check_win(AI):
                st.session_state.game_over = True
                st.session_state.message = "😭 AI가 승리했습니다. 하드 모드는 역시 강력하네요!"
            else:
                st.session_state.current_player = PLAYER
                st.session_state.message = "당신의 턴입니다!"
    st.rerun()

st.info(st.session_state.message)

st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button {
        padding: 0px !important; height: 35px !important; width: 35px !important;
        min-width: 35px !important; border-radius: 0px !important; margin: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        val = st.session_state.board[r, c]
        label = "⚫" if val == PLAYER else ("⚪" if val == AI else " ")
        cols[c].button(label, key=f"c_{r}_{c}", on_click=play_step, args=(r, c),
                       disabled=st.session_state.game_over or val != EMPTY)
