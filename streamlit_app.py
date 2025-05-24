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
    st.header("📦 Inventory Management")

    # 1. Add New Inventory Item
    st.subheader("➕ Add New Inventory Item")
    with st.form("Add Inventory"):
        name = st.text_input("Item Name")
        category = st.selectbox("Category", ["blood tubing", "chemical", "CITOS", "dialysers", "diasafe", "machine", "needle", "other item", "spare", "surgical"])
        quantity = st.number_input("Stock Quantity", min_value=0)
        unit_price = st.number_input("Unit Price")
        submitted = st.form_submit_button("Add Item")
        if submitted:
            add_inventory_item({
                "name": name,
                "category": category,
                "stock_quantity": quantity,
                "unit_price": unit_price
            })
            st.success("✅ Item added successfully!")

    # 2. View All Items
    st.subheader("📋 All Inventory Items")
    items = get_all_inventory_items()
    for item in items:
        st.json(item)

    # 3. Search by Exact Name
    st.subheader("🔍 Search Item by Exact Name")
    with st.form("Search by Name"):
        name = st.text_input("Enter full item name:")
        if st.form_submit_button("Search"):
            results = get_inventory_item_by_name(name)
            if results:
                for i in results:
                    st.json(i)
            else:
                st.warning("No items found with that exact name.")

    # 4. Search by Partial Name
    st.subheader("🔎 Search Item by Partial Name")
    with st.form("Search by Partial Name"):
        partial = st.text_input("Enter partial item name:")
        if st.form_submit_button("Search"):
            results = search_inventory_by_partial_name(partial)
            if results:
                for i in results:
                    st.json(i)
            else:
                st.warning("No matching items found.")

    # 5. Get Items by Category
    st.subheader("📁 Filter Items by Category")
    with st.form("Search by Category"):
        selected_cat = st.selectbox("Choose category:", ["blood tubing", "chemical", "CITOS", "dialysers", "diasafe", "machine", "needle", "other item", "spare", "surgical"])
        if st.form_submit_button("Filter"):
            results = get_items_by_category(selected_cat)
            if results:
                for i in results:
                    st.json(i)
            else:
                st.warning("No items found in this category.")

    # 6. Low Stock Items
    st.subheader("⚠️ Low Stock Items")
    with st.form("Low Stock"):
        threshold = st.number_input("Threshold Quantity", min_value=1, value=10)
        if st.form_submit_button("Check"):
            results = get_low_stock_items(threshold)
            if results:
                for i in results:
                    st.json(i)
            else:
                st.info("No low stock items found.")

    # 7. Get Item by Document ID
    st.subheader("📄 Get Inventory Item by Document ID")
    with st.form("Get by ID"):
        doc_id = st.text_input("Enter Firestore Document ID:")
        if st.form_submit_button("Fetch"):
            item = get_inventory_item_by_id(doc_id)
            if item:
                st.json(item)
            else:
                st.error("No item found with this document ID.")

    # 8. Update Inventory Item
    st.subheader("✏️ Update Inventory Item")
    with st.form("Update Item"):
        update_id = st.text_input("Enter Document ID to Update:")
        updated_name = st.text_input("New Name (leave blank to skip):")
        updated_price = st.number_input("New Unit Price", value=0.0)
        update_now = st.form_submit_button("Update")
        if update_now:
            data = {}
            if updated_name:
                data["name"] = updated_name
            if updated_price > 0:
                data["unit_price"] = updated_price
            if data:
                update_inventory_item(update_id, data)
                st.success("Item updated successfully!")
            else:
                st.warning("No update fields provided.")

    # 9. Update Stock Quantity
    st.subheader("🔁 Change Stock Quantity (+/-)")
    with st.form("Stock Change"):
        stock_id = st.text_input("Enter Document ID:")
        change = st.number_input("Change in Quantity (negative for decrease)", step=1)
        if st.form_submit_button("Update Stock"):
            update_stock_quantity(stock_id, int(change))
            st.success("Stock quantity updated.")

    # 10. Delete Inventory Item
    st.subheader("🗑️ Delete Inventory Item")
    with st.form("Delete Item"):
        delete_id = st.text_input("Enter Document ID to delete:")
        if st.form_submit_button("Delete"):
            delete_inventory_item(delete_id)
            st.success("Item deleted.")

    # 11. Expiring Soon Items
    st.subheader("⏳ Items Expiring Soon")
    with st.form("Expiring Soon"):
        days = st.number_input("Show items expiring within N days:", min_value=1, value=30)
        if st.form_submit_button("Check Expiry"):
            expiring_items = get_items_expiring_soon(days)
            if expiring_items:
                for item in expiring_items:
                    st.json(item)
            else:
                st.info("No items expiring within this period.")

# ---------------- Orders ----------------
with tabs[1]:
    st.header("📄 Orders")

    # Add Order
    st.subheader("➕ Add Order")
    with st.form("Add Order"):
        client_name = st.text_input("Client Name")
        items = st.text_area("Items (comma-separated)")
        total_amount = st.number_input("Total Amount")
        order_type = st.radio("Order Type", ["Purchase", "Sell"])
        submitted = st.form_submit_button("Add Order")
        if submitted:
            order_id = add_order({
                "client_name": client_name,
                "items": [i.strip() for i in items.split(",")],
                "total_amount": total_amount,
                "order_type": order_type.lower()
            })
            st.success(f"Order added! ID: {order_id}")

    # View All Orders
    st.subheader("📋 All Orders")
    orders = get_all_orders()
    for order in orders:
        st.json(order)

    # Search by Order ID
    st.subheader("🔍 Search Order by ID")
    search_id = st.text_input("Enter Order Document ID")
    if st.button("Fetch Order"):
        from firebase_config.orders import get_order_by_id
        order = get_order_by_id(search_id)
        st.json(order if order else {"error": "Order not found"})

    # Filter by Client
    st.subheader("📂 Filter Orders by Client Name")
    client_filter = st.text_input("Client Name for Filter")
    if st.button("Get Client Orders"):
        client_orders = [o for o in orders if o.get("client_name", "").lower() == client_filter.lower()]
        for o in client_orders:
            st.json(o)

    # Filter by Status
    st.subheader("📂 Filter Orders by Status")
    status_filter = st.text_input("Status (e.g., pending, completed)")
    if st.button("Get Orders by Status"):
        from firebase_config.orders import get_orders_by_status
        status_orders = get_orders_by_status(status_filter)
        for o in status_orders:
            st.json(o)

    # Orders by Date Range
    st.subheader("📅 Get Orders by Date Range")
    from firebase_config.orders import get_orders_by_date_range
    from datetime import datetime
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    if st.button("Fetch Orders in Range"):
        start = datetime.combine(start_date, datetime.min.time())
        end = datetime.combine(end_date, datetime.max.time())
        orders_in_range = get_orders_by_date_range(start, end)
        for o in orders_in_range:
            st.json(o)

    # Total Sales in Date Range
    st.subheader("💰 Total Sales in Period")
    from firebase_config.orders import get_total_sales_in_period
    start_sales = st.date_input("Sales Start Date")
    end_sales = st.date_input("Sales End Date")
    if st.button("Calculate Sales"):
        start = datetime.combine(start_sales, datetime.min.time())
        end = datetime.combine(end_sales, datetime.max.time())
        total = get_total_sales_in_period(start, end)
        st.success(f"Total Sales: ₹{total:.2f}")

    # Update Order
    st.subheader("✏️ Update Order")
    update_id = st.text_input("Order ID to Update")
    update_field = st.text_input("Field to Update (e.g., total_amount)")
    update_value = st.text_input("New Value")
    if st.button("Update Order"):
        from firebase_config.orders import update_order
        try:
            value = float(update_value) if update_field == "total_amount" else update_value
            update_order(update_id, {update_field: value})
            st.success("Order updated!")
        except Exception as e:
            st.error(f"Error: {e}")

    # Delete Order
    st.subheader("❌ Delete Order")
    delete_id = st.text_input("Order ID to Delete")
    if st.button("Delete Order"):
        from firebase_config.orders import delete_order
        try:
            delete_order(delete_id)
            st.success("Order deleted!")
        except Exception as e:
            st.error(f"Error: {e}")

    # Search by Invoice Number
    st.subheader("🔎 Search by Invoice Number")
    invoice_search = st.text_input("Invoice Number")
    if st.button("Search Order by Invoice"):
        from firebase_config.orders import search_orders_by_invoice_number
        results = search_orders_by_invoice_number(invoice_search)
        for o in results:
            st.json(o)

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
