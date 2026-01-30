import streamlit as st
from gomoku_logic import GomokuGame, PLAYER, AI, EMPTY, BOARD_SIZE

# 페이지 설정
st.set_page_config(page_title="AI와 오목 대결", page_icon="⚫", layout="centered")

# 세션 상태 초기화
if 'game' not in st.session_state:
    st.session_state.game = GomokuGame()
if 'board' not in st.session_state:
    st.session_state.board = st.session_state.game.board.copy()
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'current_player' not in st.session_state:
    st.session_state.current_player = PLAYER
if 'message' not in st.session_state:
    st.session_state.message = "당신의 턴입니다. 비어있는 칸을 클릭하세요!"

st.title("⚫ AI와 오목 대결 ⚪")

# 사이드바 설정
st.sidebar.header("게임 설정")
difficulty = st.sidebar.selectbox("AI 난이도", ["easy", "medium", "hard"])
st.session_state.game.difficulty = difficulty

if st.sidebar.button("게임 재시작"):
    st.session_state.game.reset_game()
    st.session_state.board = st.session_state.game.board.copy()
    st.session_state.game_over = False
    st.session_state.current_player = PLAYER
    st.session_state.message = "새 게임이 시작되었습니다!"
    st.rerun()

# 게임 로직 처리 함수
def play_step(r, c):
    if st.session_state.game_over or st.session_state.board[r, c] != EMPTY:
        return

    # 플레이어 착수
    if st.session_state.game.make_move(r, c, PLAYER):
        st.session_state.board = st.session_state.game.board.copy()
        if st.session_state.game.check_win(PLAYER):
            st.session_state.game_over = True
            st.session_state.message = "🎉 승리했습니다! 축하드려요!"
        elif st.session_state.game.is_board_full():
            st.session_state.game_over = True
            st.session_state.message = "무승부입니다!"
        else:
            # AI 차례
            st.session_state.current_player = AI
            st.rerun()

# AI 실행 로직
if not st.session_state.game_over and st.session_state.current_player == AI:
    with st.spinner("AI가 생각 중..."):
        ai_move = st.session_state.game.ai_move()
        if ai_move:
            r, c = ai_move
            st.session_state.game.make_move(r, c, AI)
            st.session_state.board = st.session_state.game.board.copy()
            if st.session_state.game.check_win(AI):
                st.session_state.game_over = True
                st.session_state.message = "😭 AI가 이겼습니다. 다시 도전해보세요!"
            else:
                st.session_state.current_player = PLAYER
                st.session_state.message = "당신의 턴입니다!"
    st.rerun()

# --- 보드판 렌더링 ---
st.info(st.session_state.message)

# 보드판 디자인용 CSS
st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
    button {
        padding: 0px !important;
        height: 35px !important;
        width: 35px !important;
        min-width: 35px !important;
        border-radius: 0px !important;
        margin: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# 15x15 그리드 생성
for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        cell_value = st.session_state.board[r, c]
        
        # 돌 상태에 따른 아이콘 표시
        label = " "
        if cell_value == PLAYER: label = "⚫"
        elif cell_value == AI: label = "⚪"
        
        cols[c].button(
            label, 
            key=f"cell_{r}_{c}", 
            on_click=play_step, 
            args=(r, c),
            disabled=st.session_state.game_over or cell_value != EMPTY
        )
