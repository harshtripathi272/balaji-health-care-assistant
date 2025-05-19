import streamlit as st

# Page selection
page = st.sidebar.selectbox("Go to", ["Chatbot", "Inventory", "Orders", "Clients", "Suppliers"])

if page == "Chatbot":
    st.title("AI Chat Assistant")
    user_input = st.text_input("Ask something...")
    if st.button("Send"):
        st.write("🧠 Bot Reply: (Coming soon...)")

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
