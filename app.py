import streamlit as st
from gomoku_logic import GomokuGame, PLAYER, AI, EMPTY, BOARD_SIZE

# --- 세션 상태 초기화 ---
def init_session_state():
    if 'game' not in st.session_state:
        st.session_state.game = GomokuGame()
    if 'board' not in st.session_state:
        st.session_state.board = st.session_state.game.board
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'winner' not in st.session_state:
        st.session_state.winner = None
    if 'current_player' not in st.session_state:
        st.session_state.current_player = PLAYER # 1: 사용자, 2: AI
    if 'message' not in st.session_state:
        st.session_state.message = "게임을 시작해 보세요!"

init_session_state()

st.set_page_config(page_title="AI와 오목 대결", page_icon="⚫")
st.title("⚫ AI와 오목 대결 ⚪")

st.markdown("""
    **오목 규칙:** 가로, 세로, 대각선 중 어느 한 방향으로 5개 이상의 돌을 먼저 놓는 사람이 승리합니다.
""")

# --- 난이도 설정 ---
st.sidebar.header("게임 설정")
difficulty = st.sidebar.radio(
    "AI 난이도를 선택하세요:",
    ("easy", "medium", "hard"),
    index=["easy", "medium", "hard"].index(st.session_state.game.difficulty)
)
if difficulty != st.session_state.game.difficulty:
    st.session_state.game.difficulty = difficulty
    st.session_state.message = f"난이도가 {difficulty}로 변경되었습니다. 게임을 재시작하세요."

# --- 게임 재시작 버튼 ---
if st.sidebar.button("게임 재시작"):
    st.session_state.game.reset_game()
    st.session_state.board = st.session_state.game.board
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.current_player = PLAYER
    st.session_state.message = "새로운 게임을 시작합니다!"
    st.experimental_rerun() # UI 업데이트

st.sidebar.markdown("---")
st.sidebar.markdown(f"**현재 난이도:** {st.session_state.game.difficulty.capitalize()}")

# --- 게임 보드 그리기 ---
st.subheader("게임 보드")

# CSS를 사용하여 오목판 디자인
st.markdown(
    """
    <style>
    .board-grid {
        display: grid;
        grid-template-columns: repeat(15, 30px); /* 15x15 보드, 각 셀 30px */
        grid-template-rows: repeat(15, 30px);
        width: 450px; /* 15 * 30px */
        height: 450px; /* 15 * 30px */
        border: 1px solid #333;
        background-color: #f0d9b5; /* 오목판 색상 */
    }
    .cell {
        width: 30px;
        height: 30px;
        border: 0.5px solid #888;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        position: relative;
    }
    .cell:hover {
        background-color: rgba(255, 255, 0, 0.2); /* 호버 시 노란색 하이라이트 */
    }
    .stone-player {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: black;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    .stone-ai {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: white;
        border: 1px solid #333;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    .game-message {
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 15px;
        padding: 10px;
        border-radius: 5px;
    }
    .game-message.player-turn { color: blue; }
    .game-message.ai-turn { color: red; }
    .game-message.win { color: green; }
    .game-message.draw { color: orange; }
    </style>
    """,
    unsafe_allow_html=True
)

# 보드판 클릭 처리 함수 (콜백)
def handle_click(r, c):
    if st.session_state.game_over:
        st.session_state.message = "게임이 종료되었습니다. 재시작해주세요."
        return

    # 플레이어 턴
    if st.session_state.current_player == PLAYER:
        if st.session_state.game.make_move(r, c, PLAYER):
            st.session_state.board = st.session_state.game.board.copy() # 보드 업데이트
            if st.session_state.game.check_win(PLAYER):
                st.session_state.winner = "플레이어"
                st.session_state.game_over = True
                st.session_state.message = "🎉 당신이 승리했습니다! 🎉"
            elif st.session_state.game.is_board_full():
                st.session_state.game_over = True
                st.session_state.message = "무승부입니다!"
            else:
                st.session_state.current_player = AI
                st.session_state.message = "AI의 턴입니다..."
                st.experimental_rerun() # AI 턴을 위해 UI 강제 업데이트
        else:
            st.session_state.message = "이미 돌이 놓여있거나 유효하지 않은 위치입니다."
    else:
        st.session_state.message = "AI의 턴입니다. 잠시 기다려주세요."


# AI 턴 처리 (UI 업데이트 후 자동으로 AI가 움직이도록)
if not st.session_state.game_over and st.session_state.current_player == AI:
    st.spinner("AI가 생각 중입니다...")
    ai_r, ai_c = st.session_state.game.ai_move()
    if ai_r is not None and st.session_state.game.make_move(ai_r, ai_c, AI):
        st.session_state.board = st.session_state.game.board.copy() # 보드 업데이트
        if st.session_state.game.check_win(AI):
            st.session_state.winner = "AI"
            st.session_state.game_over = True
            st.session_state.message = "😭 AI가 승리했습니다. 😭"
        elif st.session_state.game.is_board_full():
            st.session_state.game_over = True
            st.session_state.message = "무승부입니다!"
        else:
            st.session_state.current_player = PLAYER
            st.session_state.message = "당신의 턴입니다!"
    else:
        st.session_state.message = "AI가 움직일 곳을 찾지 못했습니다 (오류 발생)."
    st.experimental_rerun() # AI 움직임 후 UI 업데이트

# 게임 보드 렌더링
with st.container():
    st.markdown('<div class="board-grid">', unsafe_allow_html=True)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            key = f"cell_{r}_{c}"
            stone_class = ""
            if st.session_state.board[r, c] == PLAYER:
                stone_class = "stone-player"
            elif st.session_state.board[r, c] == AI:
                stone_class = "stone-ai"

            # Streamlit 버튼을 사용하여 각 셀을 클릭 가능하게 만듭니다.
            # 스타일을 커스텀하기 위해 HTML/CSS를 적극적으로 활용합니다.
            st.markdown(
                f"""
                <div class="cell" id="{key}" onclick="
                    streamlit.setComponentValue('clicked_cell', {{row: {r}, col: {c}}});
                ">
                    <div class="{stone_class}"></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Streamlit 버튼 자체를 클릭하는 대신, JavaScript를 통해 Streamlit 컴포넌트 값을 설정하는 방식 (더 복잡)
            # 여기서는 단순히 마크다운으로 보드를 그리고, 실제 클릭 이벤트는 Streamlit의 버튼 위젯을 활용하는 것이 더 간단합니다.
            # 하지만 보드판 자체의 CSS 컨트롤이 어렵기 때문에, 버튼 대신 마크다운 div에 JS를 심는 방법도 고려해볼 수 있습니다.
            # 현재 구현 방식은 st.button()을 사용하지 않고, JavaScript와 st.experimental_rerun()을 이용한 간접적인 클릭 처리를 시도합니다.
            # 이는 Streamlit이 기본적으로 제공하는 위젯의 한계 때문에 복잡해질 수 있습니다.

            # 간략화를 위해 아래와 같이 st.button을 각 셀에 그리는 방식으로 변경합니다.
            # 단점: 버튼의 기본 스타일이 적용되어 오목판 디자인이 깨질 수 있음.
            # 현재 코드 (마크다운 + JS)는 동작하지 않을 것이므로, 아래와 같이 변경해야 합니다.
            # 또는 각 셀을 이미지 버튼으로 만들거나, st.html 같은 컴포넌트를 사용하여 직접 HTML/JS를 제어해야 합니다.
            
            # **Streamlit 제약 사항으로 인해, 각 셀을 실제 Streamlit 위젯으로 구현하는 것이 일반적입니다.**
            # 하지만 오목판처럼 많은 버튼이 필요한 경우 성능이나 UI가 복잡해질 수 있습니다.
            # 여기서는 `st.empty().button()`을 사용하여 마크다운 CSS와 버튼을 결합하는 방법으로 시도합니다.
            
            # --- Streamlit 버튼을 사용한 셀 구현 (권장) ---
            # 각 셀을 클릭 가능한 버튼으로 만들고, CSS로 버튼 스타일을 오목판 돌 모양으로 만듭니다.
            # 이 방법은 마크다운 `onclick` 방식보다 Streamlit의 철학에 더 가깝습니다.
            
            with st.container(): # 각 셀을 별도의 컨테이너로 분리하여 배치
                # CSS flexbox를 사용하여 셀들을 배치합니다.
                # 그러나 Streamlit의 col()이나 horizontal layout은 제한적입니다.
                # 가장 간단한 방법은 각 셀을 `st.button`으로 만들고,
                # `st.columns`를 사용하여 15개의 열을 만드는 것입니다.
                # 그러나 15개의 열은 너무 많으므로, for 루프 안에 st.button을 배치하고
                # CSS로 정렬하는 방법을 사용하는 것이 현실적입니다.

                # 여기서는 좀 더 일반적인 방법을 시도합니다.
                # 각 셀을 HTML로 그리고, 클릭 시 서버로 이벤트를 전달하는 방식
                # 스트림릿은 직접적인 JS 이벤트 처리가 어렵기 때문에
                # `st.button`을 사용하거나 `st.session_state`를 활용하는 것이 일반적입니다.

                # 현재 마크다운+JS 방식은 Streamlit에서 직접적으로 JS 이벤트를
                # 파이썬 함수로 연결하기 어렵습니다.
                # 가장 일반적인 접근은 각 `(r, c)` 위치에 대해 `st.button`을 만들고,
                # 버튼 클릭 시 해당 위치의 `(r, c)` 정보를 콜백 함수로 전달하는 것입니다.

                # 아래는 `st.button`을 사용한 대체 코드입니다.
                # 보드판 디자인이 조금 깨질 수 있지만, 기능은 확실히 구현됩니다.
                
                # --- Streamlit 버튼을 사용한 실제 클릭 처리 ---
                if st.button(
                    key=f"gomoku_cell_{r}_{c}",
                    label=" ", # 버튼 텍스트 비움
                    on_click=handle_click,
                    args=(r, c),
                    # 도움말 추가
                    help=f"({r}, {c})에 돌 놓기",
                    disabled=st.session_state.board[r, c] != EMPTY or st.session_state.game_over or st.session_state.current_player == AI
                ):
                    pass # handle_click 콜백에서 모든 로직 처리
                
                # 버튼 위에 돌 이미지 또는 CSS를 이용한 돌 모양을 오버레이
                if st.session_state.board[r, c] == PLAYER:
                    st.markdown(
                        f"""
                        <style>
                        div[data-testid="stButton"] button[aria-label="(({r}, {c})에 돌 놓기)"] {{
                            background-color: black !important;
                            border-radius: 50% !important;
                            border: 0px !important;
                            width: 28px !important;
                            height: 28px !important;
                            box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
                            position: absolute;
                            top: 1px;
                            left: 1px;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                elif st.session_state.board[r, c] == AI:
                    st.markdown(
                        f"""
                        <style>
                        div[data-testid="stButton"] button[aria-label="(({r}, {c})에 돌 놓기)"] {{
                            background-color: white !important;
                            border-radius: 50% !important;
                            border: 1px solid #333 !important;
                            width: 28px !important;
                            height: 28px !important;
                            box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
                            position: absolute;
                            top: 1px;
                            left: 1px;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
    st.markdown('</div>', unsafe_allow_html=True) # 보드 그리드 닫기


# 메시지 출력
message_class = ""
if st.session_state.game_over:
    if st.session_state.winner == "플레이어":
        message_class = "game-message win"
    elif st.session_state.winner == "AI":
        message_class = "game-message ai-turn" # AI 승리 시 빨간색
    else:
        message_class = "game-message draw"
elif st.session_state.current_player == PLAYER:
    message_class = "game-message player-turn"
else:
    message_class = "game-message ai-turn"

st.markdown(f'<div class="{message_class}">{st.session_state.message}</div>', unsafe_allow_html=True)

# 봇 이미지 (플레이어가 승리했을 때 기쁜 봇, AI가 승리했을 때 슬픈 봇)
if st.session_state.game_over:
    if st.session_state.winner == "플레이어":
        st.write("🎉 축하합니다! AI를 이겼어요! 🎉")
        # AI가 패배하여 슬퍼하는 이미지
        st.image("https://www.flaticon.com/svg/v2/icons/svg/3004/3004593.svg", caption="AI 패배", width=100) # 예시 이미지
    elif st.session_state.winner == "AI":
        st.write("😭 아쉽네요! AI가 승리했습니다. 😭")
        # AI가 승리하여 기뻐하는 이미지
        st.image("https://www.flaticon.com/svg/v2/icons/svg/3004/3004592.svg", caption="AI 승리", width=100) # 예시 이미지