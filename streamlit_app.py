import streamlit as st
from firebase_config.inventory import (
    add_inventory_item, get_all_inventory_items
)
from firebase_config.orders import (
    add_order, get_all_orders
)
from firebase_config.clients import (
    add_client, get_all_clients
)
from firebase_config.suppliers import (
    add_supplier, get_all_suppliers
)
from firebase_config.invoices import (
    add_invoice, get_all_invoices
)

st.set_page_config(page_title="AI Business Assistant", layout="wide")

tabs = st.tabs(["Inventory", "Orders", "Clients", "Suppliers", "Invoices"])

# ---------------- Inventory ----------------
with tabs[0]:
    st.header("📦 Inventory")

    with st.form("Add Inventory"):
        name = st.text_input("Item Name")
        category = st.selectbox("Category", ["blood tubing", "chemical", "CITOS", "dialysers", "diasafe", "machine", "needle", "other item", "spare", "surgical"])
        quantity = st.number_input("Quantity", min_value=0)
        unit_price = st.number_input("Unit Price")
        submitted = st.form_submit_button("Add Item")
        if submitted:
            add_inventory_item({
                "name": name,
                "category": category,
                "quantity": quantity,
                "unit_price": unit_price
            })
            st.success("Item added!")

    st.subheader("All Inventory Items")
    items = get_all_inventory_items()
    for item in items:
        st.json(item)

# ---------------- Orders ----------------
with tabs[1]:
    st.header("📄 Orders")

    with st.form("Add Order"):
        client_name = st.text_input("Client Name")
        items = st.text_area("Items (comma-separated)")
        total_amount = st.number_input("Total Amount")
        order_type = st.radio("Order Type", ["Purchase", "Sell"])
        submitted = st.form_submit_button("Add Order")
        if submitted:
            add_order({
                "client_name": client_name,
                "items": [i.strip() for i in items.split(",")],
                "total_amount": total_amount,
                "order_type": order_type.lower()
            })
            st.success("Order added!")

    st.subheader("All Orders")
    orders = get_all_orders()
    for order in orders:
        st.json(order)

# ---------------- Clients ----------------
with tabs[2]:
    st.header("👥 Clients")

    with st.form("Add Client"):
        name = st.text_input("Client Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Add Client")
        if submitted:
            add_client({
                "name": name,
                "email": email,
                "phone": phone
            })
            st.success("Client added!")

    st.subheader("All Clients")
    clients = get_all_clients()
    for client in clients:
        st.json(client)

# ---------------- Suppliers ----------------
with tabs[3]:
    st.header("🏭 Suppliers")

    with st.form("Add Supplier"):
        name = st.text_input("Supplier Name")
        contact_person = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        items = st.text_area("Items Supplied (comma-separated)")
        submitted = st.form_submit_button("Add Supplier")
        if submitted:
            add_supplier({
                "name": name,
                "contact_person": contact_person,
                "phone": phone,
                "items_supplied": [i.strip() for i in items.split(",")]
            })
            st.success("Supplier added!")

    st.subheader("All Suppliers")
    suppliers = get_all_suppliers()
    for supplier in suppliers:
        st.json(supplier)

# ---------------- Invoices ----------------
with tabs[4]:
    st.header("📑 Invoices")

    with st.form("Add Invoice"):
        invoice_no = st.text_input("Invoice Number")
        date = st.date_input("Date")
        amount = st.number_input("Amount")
        related_order = st.text_input("Related Order Info")
        submitted = st.form_submit_button("Add Invoice")
        if submitted:
            add_invoice({
                "invoice_no": invoice_no,
                "date": str(date),
                "amount": amount,
                "related_order": related_order
            })
            st.success("Invoice added!")

    st.subheader("All Invoices")
    invoices = get_all_invoices()
    for invoice in invoices:
        st.json(invoice)
