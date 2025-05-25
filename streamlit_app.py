import streamlit as st
from firebase_config.inventory import (
    add_inventory_item, get_all_inventory_items, get_inventory_item_by_id, delete_inventory_item, get_items_by_category, get_items_expiring_soon
    , get_low_stock_items, search_inventory_by_partial_name, update_inventory_item, update_stock_quantity
)
from firebase_config.orders import (
    add_order, get_all_orders
)
from firebase_config.clients import (
    add_client, get_all_clients, delete_client, get_client_by_id, get_client_by_name, get_client_order_history, get_client_payments, search_clients_by_partial_name, update_client, update_client_due
)

from firebase_config.invoices import (
    add_invoice, get_all_invoices, delete_invoice, get_invoice_by_id, get_invoice_by_number, update_invoice
)
from firebase_config.finance import add_expense, add_payment, add_supplier_payment, delete_expense, get_all_dues,get_expenses, get_payments, get_supplier_payments, get_total_expenses, get_total_payments, update_client_due, update_expense

st.set_page_config(page_title="AI Business Assistant", layout="wide")

tabs = st.tabs(["Inventory", "Orders", "Clients", "Suppliers", "Invoices", "Finanace"])

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
            from firebase_config.inventory import get_inventory_item_by_name
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

    # --- Add Client Form ---
    with st.form("Add Client"):
        name = st.text_input("Client Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Add Client")
        if submitted:
            client_id = add_client({
                "name": name,
                "email": email,
                "phone": phone,
                "total_due": 0.0
            })
            st.success(f"Client added! ID: {client_id}")

    # --- View All Clients ---
    st.subheader("📋 All Clients")
    clients = get_all_clients()
    for client in clients:
        st.json(client)

    client_names = [client["name"] for client in clients]
    selected_name = st.selectbox("Select a client to view details", client_names)

    selected_client = next((c for c in clients if c["name"] == selected_name), None)
    if selected_client:
        st.write("### Client Info")
        st.json(selected_client)

        # Show order history
        st.write("### Order History")
        order_history = get_client_order_history(selected_client["id"])
        if order_history:
            for order in order_history:
                st.json(order)
        else:
            st.info("No orders found for this client.")

    # --- Search Client by Exact Name ---
    st.subheader("🔍 Search Client by Name")
    with st.form("Search Client Name"):
        search_name = st.text_input("Enter full client name")
        if st.form_submit_button("Search"):
            results = get_client_by_name(search_name)
            for r in results:
                st.json(r)

    # --- Search Client by Partial Name ---
    st.subheader("🔍 Search Client by Partial Name")
    with st.form("Search Partial"):
        partial_name = st.text_input("Enter partial name")
        if st.form_submit_button("Search"):
            results = search_clients_by_partial_name(partial_name)
            for r in results:
                st.json(r)

    # --- View & Update a Specific Client by ID ---
    st.subheader("✏️ Update Client Info")
    with st.form("Update Client"):
        client_id = st.text_input("Client ID to update")
        new_name = st.text_input("New Name")
        new_email = st.text_input("New Email")
        new_phone = st.text_input("New Phone")
        if st.form_submit_button("Update"):
            update_client(client_id, {
                "name": new_name,
                "email": new_email,
                "phone": new_phone
            })
            st.success("Client updated!")

    # --- Delete Client ---
    st.subheader("❌ Delete Client")
    with st.form("Delete Client"):
        delete_id = st.text_input("Client ID to delete")
        if st.form_submit_button("Delete"):
            delete_client(delete_id)
            st.warning("Client deleted!")

    # --- View Client Order History ---
    st.subheader("📦 View Client Order History")
    with st.form("Client Orders"):
        order_client_id = st.text_input("Client ID for orders")
        if st.form_submit_button("Show Orders"):
            orders = get_client_order_history(order_client_id)
            for o in orders:
                st.json(o)

    # --- View Client Payments ---
    st.subheader("💵 View Client Payments")
    with st.form("Client Payments"):
        payment_client_id = st.text_input("Client ID for payments")
        if st.form_submit_button("Show Payments"):
            payments = get_client_payments(payment_client_id)
            for p in payments:
                st.json(p)

    # --- Update Client Due ---
    st.subheader("💰 Update Client Due")
    with st.form("Update Due"):
        due_client_id = st.text_input("Client ID to update due")
        due_change = st.number_input("Change in due (positive or negative)", step=0.01)
        if st.form_submit_button("Update Due"):
            update_client_due(due_client_id, due_change)
            st.success("Client due updated.")


# ---------------- Suppliers ----------------
from firebase_config.suppliers import (
    add_supplier, get_all_suppliers, get_supplier_by_name,
    search_suppliers_by_partial_name, get_supplier_order_history,
    get_supplier_payments, update_supplier_due, update_supplier, delete_supplier
)

with tabs[3]:
    st.header("🏭 Suppliers")

    # ---------- Add Supplier Form ----------
    with st.form("Add Supplier"):
        st.subheader("➕ Add New Supplier")
        name = st.text_input("Supplier Name")
        contact_person = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        items = st.text_area("Items Supplied (comma-separated)")
        submitted = st.form_submit_button("Add Supplier")
        if submitted:
            supplier_data = {
                "name": name,
                "contact_person": contact_person,
                "phone": phone,
                "items_supplied": [i.strip() for i in items.split(",")],
                "total_due": 0.0
            }
            add_supplier(supplier_data)
            st.success("✅ Supplier added successfully!")

    # ---------- All Suppliers ----------
    st.subheader("📋 All Suppliers")
    suppliers = get_all_suppliers()
    for supplier in suppliers:
        with st.expander(f"🔍 {supplier['name']}"):
            st.write(supplier)

            # Order History
            st.markdown("**📦 Order History**")
            history = get_supplier_order_history(supplier["id"])
            for order in history:
                st.json(order)

            # Payment History
            st.markdown("**💵 Payment History**")
            payments = get_supplier_payments(supplier["id"])
            for p in payments:
                st.json(p)

            # Update Due
            st.markdown("**➕➖ Update Due Amount**")
            due_change = st.number_input(f"Change due for {supplier['name']}", step=100.0, key=f"due_{supplier['id']}")
            if st.button("Update Due", key=f"update_due_{supplier['id']}"):
                update_supplier_due(supplier["id"], due_change)
                st.success("✅ Due updated!")

            # Update Supplier Details
            st.markdown("**✏️ Update Supplier Info**")
            new_phone = st.text_input("New Phone", value=supplier["phone"], key=f"phone_{supplier['id']}")
            new_contact = st.text_input("New Contact Person", value=supplier["contact_person"], key=f"contact_{supplier['id']}")
            if st.button("Update Supplier", key=f"edit_{supplier['id']}"):
                update_supplier(supplier["id"], {
                    "phone": new_phone,
                    "contact_person": new_contact
                })
                st.success("✅ Supplier info updated!")

            # Delete Supplier
            if st.button("🗑️ Delete Supplier", key=f"delete_{supplier['id']}"):
                delete_supplier(supplier["id"])
                st.warning("⚠️ Supplier deleted. Refresh the page.")

    # ---------- Search by Exact Name ----------
    st.subheader("🔍 Search Supplier by Name")
    with st.form("Search Supplier Exact"):
        name_search = st.text_input("Enter exact name")
        if st.form_submit_button("Search"):
            results = get_supplier_by_name(name_search)
            for r in results:
                st.json(r)

    # ---------- Search by Partial Name ----------
    st.subheader("🔎 Search Supplier by Partial Name")
    with st.form("Search Supplier Partial"):
        partial_search = st.text_input("Enter partial name")
        if st.form_submit_button("Search"):
            results = search_suppliers_by_partial_name(partial_search)
            for r in results:
                st.json(r)


# ---------------- Invoices ----------------
with tabs[4]:
    # Add Invoice Form
    with st.form("Add Invoice"):
        st.subheader("Add New Invoice")
        invoice_number = st.text_input("Invoice Number")
        client_id = st.text_input("Client ID")
        client_name = st.text_input("Client Name")
        date = st.date_input("Invoice Date", value=datetime.today())
        items_raw = st.text_area("Items (JSON format)", help='Example: [{"item_name":"Bizaic","quantity":1,"unit_price":60000}]')
        total_amount = st.number_input("Total Amount", min_value=0.0, format="%.2f")
        status = st.selectbox("Status", ["paid", "pending", "overdue"])

        submitted = st.form_submit_button("Add Invoice")
        if submitted:
            try:
                import json
                items = json.loads(items_raw)
                invoice_data = {
                    "invoice_number": invoice_number,
                    "client_id": client_id,
                    "client_name": client_name,
                    "date": date.isoformat(),
                    "items": items,
                    "total_amount": total_amount,
                    "status": status,
                }
                invoice_id = add_invoice(invoice_data)
                st.success(f"Invoice added with ID: {invoice_id}")
            except Exception as e:
                st.error(f"Error adding invoice: {e}")

    st.subheader("All Invoices")
    invoices = get_all_invoices()
    for invoice in invoices:
        st.json(invoice)

    st.subheader("Search Invoice by Number")
    with st.form("Search Invoice"):
        search_invoice_number = st.text_input("Enter Invoice Number")
        search_submitted = st.form_submit_button("Search")
        if search_submitted:
            found_invoices = get_invoice_by_number(search_invoice_number)
            if found_invoices:
                for inv in found_invoices:
                    st.json(inv)
            else:
                st.info("No invoices found with that number.")

    st.subheader("Update Invoice")
    with st.form("Update Invoice"):
        update_id = st.text_input("Invoice Document ID")
        update_field = st.text_input("Field to Update (e.g., status, total_amount)")
        update_value = st.text_input("New Value")
        update_submitted = st.form_submit_button("Update")
        if update_submitted:
            try:
                # Convert update_value type if needed (simple heuristic)
                if update_field in ["total_amount"]:
                    update_value_casted = float(update_value)
                else:
                    update_value_casted = update_value
                update_invoice(update_id, {update_field: update_value_casted})
                st.success("Invoice updated successfully!")
            except Exception as e:
                st.error(f"Failed to update invoice: {e}")

    st.subheader("Delete Invoice")
    with st.form("Delete Invoice"):
        delete_id = st.text_input("Invoice Document ID to Delete")
        delete_submitted = st.form_submit_button("Delete")
        if delete_submitted:
            try:
                delete_invoice(delete_id)
                st.success("Invoice deleted successfully!")
            except Exception as e:
                st.error(f"Failed to delete invoice: {e}")

with tabs[5]:
    st.header("💰 Finance Overview")

    # --- Add Payment ---
    st.subheader("📥 Record Client Payment")
    with st.form("Add Payment"):
        client_id = st.text_input("Client ID")
        amount = st.number_input("Amount", min_value=0.0)
        invoice_id = st.text_input("Invoice ID (optional)")
        payment_method = st.selectbox("Payment Method", ["cash", "bank transfer", "UPI", "other"])
        notes = st.text_area("Notes", "")
        submitted = st.form_submit_button("Record Payment")
        if submitted:
            from firebase_config.finance import add_payment, update_client_due
            from google.cloud import firestore
            add_payment({
                "client_id": client_id,
                "amount": amount,
                "date": firestore.SERVER_TIMESTAMP,
                "invoice_id": invoice_id,
                "payment_method": payment_method,
                "notes": notes
            })
            update_client_due(client_id, -amount)
            st.success("Payment recorded and due updated!")

    # --- Add Expense ---
    st.subheader("📤 Record Expense")
    with st.form("Add Expense"):
        category = st.selectbox("Category", ["rent", "electricity", "salary", "supplies", "transport", "other"])
        amount = st.number_input("Expense Amount", min_value=0.0, key="expense_amount")
        paid_to = st.text_input("Paid To")
        description = st.text_area("Description")
        submit_expense = st.form_submit_button("Record Expense")
        if submit_expense:
            from firebase_config.finance import add_expense
            from google.cloud import firestore
            add_expense({
                "category": category,
                "amount": amount,
                "date": firestore.SERVER_TIMESTAMP,
                "paid_to": paid_to,
                "description": description
            })
            st.success("Expense recorded!")

    # --- View Dues ---
    st.subheader("📋 Clients with Dues")
    from firebase_config.finance import get_all_dues
    dues = get_all_dues()
    if dues:
        for d in dues:
            st.markdown(f"**{d['name']}** (Due: ₹{d['total_due']})")
    else:
        st.info("No dues found.")

    # --- View Payments ---
    st.subheader("🧾 All Client Payments")
    from firebase_config.finance import get_payments
    payments = get_payments()
    for p in payments:
        st.json(p)

    # --- View Expenses ---
    st.subheader("📉 All Expenses")
    from firebase_config.finance import get_expenses
    expenses = get_expenses()
    for e in expenses:
        st.json(e)

    # --- Finance Summary ---
    st.subheader("📊 Financial Summary")
    from firebase_config.finance import get_total_payments, get_total_expenses
    total_in = get_total_payments()
    total_out = get_total_expenses()
    net = total_in - total_out
    st.markdown(f"""
        - 💸 **Total Payments Received:** ₹{total_in}
        - 📤 **Total Expenses:** ₹{total_out}
        - 💼 **Net Balance:** ₹{net}
    """)
