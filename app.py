import streamlit as st
from Chatbot.chatbot import handle_user_input



# Page selection
page = st.sidebar.selectbox("Go to", ["Chatbot", "Inventory", "Orders", "Clients", "Suppliers"])

if page == "Chatbot":
    st.title("AI Chat Assistant")

    
    



    user_query = st.text_input("Ask your assistant:")

    



    if st.button("Send"):
        if user_query:
            result = handle_user_input(user_query)
            st.write("Response:")
            st.write(result)

elif page == "Inventory":
    st.title("Inventory Management")
    st.write("📦 Current inventory: Loading from Firebase...")

elif page == "Orders":
    st.title("Order Management")
    st.write("📝 List of Orders: Fetching from Firebase...")

elif page == "Clients":
    st.title("Client Records")
    st.write("👤 Clients data coming soon...")

elif page == "Suppliers":
    st.title("Supplier Records")
    st.write("🚚 Suppliers data coming soon...")
