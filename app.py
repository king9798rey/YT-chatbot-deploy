import streamlit as st
from yt import build_chain

st.title("🎥 YouTube ChatBot")

st.write("""
1. Paste YouTube Video ID
2. Ask question about the video
""")

video_id = st.text_input("Paste Video ID")

question = st.text_input("Ask Question")

if st.button("Execute"):

    if not video_id:
        st.error("Please enter Video ID")

    elif not question:
        st.error("Please enter Question")

    else:
        with st.spinner("Processing..."):

            try:
                main_chain = build_chain(video_id)

                if main_chain is None:
                    st.error("Could not create chatbot.")
                else:
                    response = main_chain.invoke(question)
                    st.success("Answer Generated")
                    st.write(response)

            except Exception as e:
                st.error(str(e))
                