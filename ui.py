import datetime
import time

import streamlit as st

st.set_page_config(
    page_title="Arabic Context Game",
    page_icon="🏠",
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug": "https://github.com/mtami/arabic-context/issues/new/choose",
        "About": """
         Simple game to guess secret arabic words using pre-trained [aravec](https://github.com/bakrianoo/aravec) model.\n
         Inspired by the English version [Contexto](https://contexto.me/).
    """,
    },
)


from model import calculate_distance

today = datetime.date.today()
day_one = datetime.date(2023, 2, 1)


def main():
    def comp_factory(val: int):
        if val in range(0, 100):
            return st.info
        elif val in range(101, 1000):
            return st.warning
        else:
            return st.error

    def update_game_day():
        # make sure the user pick another date
        if st.session_state.input_date != add_date_input:
            st.session_state.user_query = ""
            st.session_state.prev_game = st.session_state.game
            st.session_state.game = (st.session_state.input_date - day_one).days

    def update_state(user_query):
        user_queries = [
            q["word"] for q in st.session_state.lookup[game]["query_history"]
        ]
        if user_query in user_queries:
            st.warning(f"The word {user_query} was already guessed.", icon="⚠️")
        else:
            success, data = calculate_distance(day=game, word=user_query)
            st.session_state.lookup[game]["query_history"].append(
                {**data, **{"word": user_query}}
            )

            if success:
                st.session_state.lookup[game]["guess"] += 1
                guess_count = st.session_state.lookup[game]["guess"]
                if data["distance"] == 0:
                    st.success(
                        f"Congrats! You got the word in {guess_count} guesses", icon="✅"
                    )
                    # st.session_state.user_query_disabled = True
                    st.balloons()
                    # st.experimental_rerun()

            else:
                st.error(data["detail"], icon="🤖")

    if "game" not in st.session_state:
        st.session_state.game = (today - day_one).days

    game = st.session_state.game

    if "lookup" not in st.session_state:
        st.session_state.lookup = {}

    if game not in st.session_state.lookup:
        st.session_state.lookup[game] = {"guess": 0, "query_history": []}

    game_title = st.title("Guess the Word of Today")
    game_info = st.subheader(
        f"Day: #{game+1}  GUESSES: {st.session_state.lookup[game]['guess']}"
    )
    user_query = st.text_input(
        "Guess",
        placeholder="type a word",
        key="user_query",
        label_visibility="collapsed",
        disabled=getattr(st.session_state, "user_query_disabled", False),
    )

    if st.session_state.user_query:
        with st.spinner("Wait for it..."):
            time.sleep(1)
            try:
                update_state(user_query)
            except Exception as e:
                st.error("Something went wrong!", icon="🚨")
                print(e)

    for query in st.session_state.lookup[game]["query_history"]:
        if "distance" in query.keys():
            word = query["word"]
            distance = query["distance"]
            comp_factory(distance)(f"{word}  #{distance}")

            # st.progress(q['distance'])

    with st.sidebar:
        add_date_input = st.date_input(
            "Previous Words",
            value=today,
            min_value=day_one,
            max_value=today,
            key="input_date",
            on_change=update_game_day,
        )

        languages = st.selectbox(
            "Select Language?",
            ("Arabic",),
        )

        """
        ℹ️ How To Play?\n
        Find the secret word.
        You have unlimited guesses.
        The words were sorted 
        by an artificial intelligence algorithm 
        according to how similar they were to the secret word.
        After submitting a word,
        you will see its position.
        The secret word is number 1.
        The algorithm analyzed thousands of texts.
        It uses the context in which words
         are used to calculate the similarity between them.
        """


if __name__ == "__main__":
    main()
