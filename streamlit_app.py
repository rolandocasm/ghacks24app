import streamlit as st
from PIL import Image
import io
import base64
from openai import OpenAI


# Sample book data (replace with actual book paths and content)
books = {
    "Book 1": {"content": "Page 1 of Book 1...\nPage 2 of Book 1...", "page_count": 2, "image": "book1.jpg"},
    "Book 2": {"content": "Page 1 of Book 2...\nPage 2 of Book 2...", "page_count": 2, "image": "book2.jpg"},
    "Book 3": {"content": "Page 1 of Book 3...\nPage 2 of Book 3...", "page_count": 2, "image": "book3.jpg"},
    # ...add more books as needed
}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Set page title
st.set_page_config(page_title="Book Viewer", page_icon=":books:")

# Persistent Chat Sidebar
with st.sidebar:
    st.title("Gemini Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    chat_container = st.container()

    if prompt := chat_container.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            chat_container.markdown(prompt)

        with chat_container.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            ## Here we should add the code to call Gemini API
            response = chat_container.write("This is Gemini's Response")
        st.session_state.messages.append({"role": "assistant", "content": response})

# Main content area
st.title("Book Viewer")

# Initialize session state for selected book and page
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None
if "page_number" not in st.session_state:
    st.session_state.page_number = 1

# Display book images in a grid
cols = st.columns(3)
book_count = 0
for book_title, book_info in books.items():
    with cols[book_count % 3]:
        img = Image.open(book_info["image"])
        img = img.resize((200, 300))

        # Convert the image to bytes and encode it as base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Display the image and the button underneath it.
        st.markdown(
            f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{img_str}" alt="{book_title}" style="width:100%"></div>',
            unsafe_allow_html=True,
        )
        if st.button(book_title, key=book_title):
            # Update session state when the button is clicked
            if st.session_state.selected_book == book_title:
                st.session_state.selected_book = None
                st.session_state.page_number = 1
            else:
                st.session_state.selected_book = book_title
                st.session_state.page_number = 1

            st.cache_resource.clear()  # Invalidate cache

    book_count += 1
    if book_count >= 12:
        break

# Display selected book content
if st.session_state.selected_book:
    book = books[st.session_state.selected_book]
    
    page_number = st.number_input(
        "Page",
        min_value=1,
        max_value=book["page_count"],
        value=st.session_state.page_number,
        key=f"page_number_{st.session_state.selected_book}",
    )

    st.session_state.page_number = page_number

    page_content = book["content"].split("\n")[page_number - 1]
    st.subheader(f"Reading: {st.session_state.selected_book}")
    st.markdown(page_content)

