import streamlit as st
from Data.orders import get_orders, add_orders, update_orders

st.title("📦 Order Management")

# Display existing orders
st.subheader("All Orders")
orders = get_orders()
if orders:
    for idx, order in enumerate(orders):
        st.markdown(f"**Order {idx+1}:**")
        st.json(order)
else:
    st.info("No orders found.")

# Form to add a new order
st.subheader("➕ Add New Order")
with st.form("add_order_form"):
    client_name = st.text_input("Client Name")
    product_name = st.text_input("Product Name")
    quantity = st.number_input("Quantity", min_value=1)
    price = st.number_input("Price", min_value=0.0, step=0.01)
    status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
    submitted = st.form_submit_button("Add Order")

    if submitted:
        order_data = {
            "client_name": client_name,
            "product_name": product_name,
            "quantity": quantity,
            "price": price,
            "status": status
        }
        add_orders(order_data)
        st.success("✅ Order added successfully!")

# Form to update an order
st.subheader("✏️ Update Existing Order")
with st.form("update_order_form"):
    order_id = st.text_input("Order Document ID to Update")
    new_status = st.selectbox("New Status", ["Pending", "Completed", "Cancelled"])
    update_btn = st.form_submit_button("Update Status")

    if update_btn and order_id:
        try:
            update_orders(order_id, {"status": new_status})
            st.success(f"✅ Order {order_id} updated to '{new_status}'")
        except Exception as e:
            st.error(f"❌ Failed to update order: {e}")
