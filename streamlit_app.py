import streamlit as st
import logging
from datetime import datetime
from firebase_config.agent import run_agent
from firebase_config.inventory import (
    add_inventory_item, get_all_inventory_items, get_inventory_item_by_name,
    search_inventory_by_partial_name, get_items_by_category, get_low_stock_items,
    get_inventory_item_by_id, update_inventory_item, update_stock_quantity,
    delete_inventory_item, get_items_expiring_soon
)
from firebase_config.orders import (
    add_order, get_all_orders, get_order_by_id, get_orders_by_status,
    get_orders_by_date_range, get_total_sales_in_period, update_order,
    delete_order, search_orders_by_invoice_number
)
from firebase_config.clients import (
    add_client, get_all_clients, get_client_by_name, search_clients_by_partial_name,
    update_client, delete_client, get_client_order_history, get_client_payments,
    update_client_due
)
from firebase_config.suppliers import (
    add_supplier, get_all_suppliers, get_supplier_by_name,
    search_suppliers_by_partial_name, get_supplier_order_history,
    get_supplier_payments, update_supplier_due, update_supplier, delete_supplier
)
from firebase_config.invoices import (
    add_invoice, get_all_invoices, get_invoice_by_number, update_invoice, delete_invoice
)
from firebase_config.finance import (
    add_payment, add_expense, get_all_dues, get_payments, get_expenses,
    get_total_payments, get_total_expenses
)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Business Assistant", layout="wide")

tabs = st.tabs(["Inventory", "Orders", "Clients", "Suppliers", "Invoices", "Finance", "ChatBot"])

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
            try:
                add_inventory_item({
                    "name": name,
                    "category": category,
                    "stock_quantity": quantity,
                    "unit_price": unit_price
                })
                st.success("✅ Item added successfully!")
            except Exception as e:
                logger.error(f"Error adding inventory item: {e}")
                st.error(f"Error: {e}")

    # 2. View All Items
    st.subheader("📋 All Inventory Items")
    try:
        items = get_all_inventory_items()
        for item in items:
            st.json(item)
    except Exception as e:
        logger.error(f"Error fetching inventory items: {e}")
        st.error(f"Error: {e}")

    # 3. Search by Exact Name
    st.subheader("🔍 Search Item by Exact Name")
    with st.form("Search by Name"):
        name = st.text_input("Enter full item name:")
        if st.form_submit_button("Search"):
            try:
                results = get_inventory_item_by_name(name)
                if results:
                    for i in results:
                        st.json(i)
                else:
                    st.warning("No items found with that exact name.")
            except Exception as e:
                logger.error(f"Error searching by name: {e}")
                st.error(f"Error: {e}")

    # 4. Search by Partial Name
    st.subheader("🔎 Search Item by Partial Name")
    with st.form("Search by Partial Name"):
        partial = st.text_input("Enter partial item name:")
        if st.form_submit_button("Search"):
            try:
                results = search_inventory_by_partial_name(partial)
                if results:
                    for i in results:
                        st.json(i)
                else:
                    st.warning("No matching items found.")
            except Exception as e:
                logger.error(f"Error searching by partial name: {e}")
                st.error(f"Error: {e}")

    # 5. Get Items by Category
    st.subheader("📁 Filter Items by Category")
    with st.form("Search by Category"):
        selected_cat = st.selectbox("Choose category:", ["blood tubing", "chemical", "CITOS", "dialysers", "diasafe", "machine", "needle", "other item", "spare", "surgical"])
        if st.form_submit_button("Filter"):
            try:
                results = get_items_by_category(selected_cat)
                if results:
                    for i in results:
                        st.json(i)
                else:
                    st.warning("No items found in this category.")
            except Exception as e:
                logger.error(f"Error filtering by category: {e}")
                st.error(f"Error: {e}")

    # 6. Low Stock Items
    st.subheader("⚠️ Low Stock Items")
    with st.form("Low Stock"):
        threshold = st.number_input("Threshold Quantity", min_value=1, value=10)
        if st.form_submit_button("Check"):
            try:
                results = get_low_stock_items(threshold)
                if results:
                    for i in results:
                        st.json(i)
                else:
                    st.info("No low stock items found.")
            except Exception as e:
                logger.error(f"Error fetching low stock items: {e}")
                st.error(f"Error: {e}")

    # 7. Get Item by Document ID
    st.subheader("📄 Get Inventory Item by Document ID")
    with st.form("Get by ID"):
        doc_id = st.text_input("Enter Firestore Document ID:")
        if st.form_submit_button("Fetch"):
            try:
                item = get_inventory_item_by_id(doc_id)
                if item:
                    st.json(item)
                else:
                    st.error("No item found with this document ID.")
            except Exception as e:
                logger.error(f"Error fetching item by ID: {e}")
                st.error(f"Error: {e}")

    # 8. Update Inventory Item
    st.subheader("✏️ Update Inventory Item")
    with st.form("Update Item"):
        update_id = st.text_input("Enter Document ID to Update:")
        updated_name = st.text_input("New Name (leave blank to skip):")
        updated_price = st.number_input("New Unit Price", value=0.0)
        update_now = st.form_submit_button("Update")
        if update_now:
            try:
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
            except Exception as e:
                logger.error(f"Error updating inventory item: {e}")
                st.error(f"Error: {e}")

    # 9. Update Stock Quantity
    st.subheader("🔁 Change Stock Quantity (+/-)")
    with st.form("Stock Change"):
        stock_id = st.text_input("Enter Document ID:")
        change = st.number_input("Change in Quantity (negative for decrease)", step=1)
        if st.form_submit_button("Update Stock"):
            try:
                update_stock_quantity(stock_id, int(change))
                st.success("Stock quantity updated.")
            except Exception as e:
                logger.error(f"Error updating stock quantity: {e}")
                st.error(f"Error: {e}")

    # 10. Delete Inventory Item
    st.subheader("🗑️ Delete Inventory Item")
    with st.form("Delete Item"):
        delete_id = st.text_input("Enter Document ID to delete:")
        if st.form_submit_button("Delete"):
            try:
                delete_inventory_item(delete_id)
                st.success("Item deleted.")
            except Exception as e:
                logger.error(f"Error deleting inventory item: {e}")
                st.error(f"Error: {e}")

    # 11. Expiring Soon Items
    st.subheader("⏳ Items Expiring Soon")
    with st.form("Expiring Soon"):
        days = st.number_input("Show items expiring within N days:", min_value=1, value=30)
        if st.form_submit_button("Check Expiry"):
            try:
                expiring_items = get_items_expiring_soon(days)
                if expiring_items:
                    for item in expiring_items:
                        st.json(item)
                else:
                    st.info("No items expiring within this period.")
            except Exception as e:
                logger.error(f"Error fetching expiring items: {e}")
                st.error(f"Error: {e}")

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
            try:
                order_id = add_order({
                    "client_name": client_name,
                    "items": [i.strip() for i in items.split(",")],
                    "total_amount": total_amount,
                    "order_type": order_type.lower()
                })
                st.success(f"Order added! ID: {order_id}")
            except Exception as e:
                logger.error(f"Error adding order: {e}")
                st.error(f"Error: {e}")

    # View All Orders
    st.subheader("📋 All Orders")
    try:
        orders = get_all_orders()
        for order in orders:
            st.json(order)
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        st.error(f"Error: {e}")

    # Search by Order ID
    st.subheader("🔍 Search Order by ID")
    search_id = st.text_input("Enter Order Document ID")
    if st.button("Fetch Order"):
        try:
            order = get_order_by_id(search_id)
            st.json(order if order else {"error": "Order not found"})
        except Exception as e:
            logger.error(f"Error fetching order by ID: {e}")
            st.error(f"Error: {e}")

    # Filter by Client
    st.subheader("📂 Filter Orders by Client Name")
    client_filter = st.text_input("Client Name for Filter")
    if st.button("Get Client Orders"):
        try:
            client_orders = [o for o in orders if o.get("client_name", "").lower() == client_filter.lower()]
            for o in client_orders:
                st.json(o)
            if not client_orders:
                st.info("No orders found for this client.")
        except Exception as e:
            logger.error(f"Error filtering orders by client: {e}")
            st.error(f"Error: {e}")

    # Filter by Status
    st.subheader("📂 Filter Orders by Status")
    status_filter = st.text_input("Status (e.g., pending, completed)")
    if st.button("Get Orders by Status"):
        try:
            status_orders = get_orders_by_status(status_filter)
            for o in status_orders:
                st.json(o)
            if not status_orders:
                st.info("No orders found with this status.")
        except Exception as e:
            logger.error(f"Error filtering orders by status: {e}")
            st.error(f"Error: {e}")

    # Orders by Date Range
    st.subheader("📅 Get Orders by Date Range")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    if st.button("Fetch Orders in Range"):
        try:
            start = datetime.combine(start_date, datetime.min.time())
            end = datetime.combine(end_date, datetime.max.time())
            orders_in_range = get_orders_by_date_range(start, end)
            for o in orders_in_range:
                st.json(o)
            if not orders_in_range:
                st.info("No orders found in this date range.")
        except Exception as e:
            logger.error(f"Error fetching orders by date range: {e}")
            st.error(f"Error: {e}")

    # Total Sales in Date Range
    st.subheader("💰 Total Sales in Period")
    start_sales = st.date_input("Sales Start Date")
    end_sales = st.date_input("Sales End Date")
    if st.button("Calculate Sales"):
        try:
            start = datetime.combine(start_sales, datetime.min.time())
            end = datetime.combine(end_sales, datetime.max.time())
            total = get_total_sales_in_period(start, end)
            st.success(f"Total Sales: ₹{total:.2f}")
        except Exception as e:
            logger.error(f"Error calculating total sales: {e}")
            st.error(f"Error: {e}")

    # Update Order
    st.subheader("✏️ Update Order")
    update_id = st.text_input("Order ID to Update")
    update_field = st.text_input("Field to Update (e.g., total_amount)")
    update_value = st.text_input("New Value")
    if st.button("Update Order"):
        try:
            value = float(update_value) if update_field == "total_amount" else update_value
            update_order(update_id, {update_field: value})
            st.success("Order updated!")
        except Exception as e:
            logger.error(f"Error updating order: {e}")
            st.error(f"Error: {e}")

    # Delete Order
    st.subheader("❌ Delete Order")
    delete_id = st.text_input("Order ID to Delete")
    if st.button("Delete Order"):
        try:
            delete_order(delete_id)
            st.success("Order deleted!")
        except Exception as e:
            logger.error(f"Error deleting order: {e}")
            st.error(f"Error: {e}")

    # Search by Invoice Number
    st.subheader("🔎 Search by Invoice Number")
    invoice_search = st.text_input("Invoice Number")
    if st.button("Search Order by Invoice"):
        try:
            results = search_orders_by_invoice_number(invoice_search)
            for o in results:
                st.json(o)
            if not results:
                st.info("No orders found with this invoice number.")
        except Exception as e:
            logger.error(f"Error searching orders by invoice: {e}")
            st.error(f"Error: {e}")

# ---------------- Clients ----------------
with tabs[2]:
    st.header("👥 Clients")

    # Add Client Form
    with st.form("Add Client"):
        name = st.text_input("Client Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Add Client")
        if submitted:
            try:
                client_id = add_client({
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "total_due": 0.0
                })
                st.success(f"Client added! ID: {client_id}")
            except Exception as e:
                logger.error(f"Error adding client: {e}")
                st.error(f"Error: {e}")

    # View All Clients
    st.subheader("📋 All Clients")
    try:
        clients = get_all_clients()
        for client in clients:
            st.json(client)
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        st.error(f"Error: {e}")

    # Select Client for Details
    client_names = [client["name"] for client in clients] if clients else []
    selected_name = st.selectbox("Select a client to view details", client_names) if client_names else st.write("No clients available.")
    if client_names and selected_name:
        selected_client = next((c for c in clients if c["name"] == selected_name), None)
        if selected_client:
            st.write("### Client Info")
            st.json(selected_client)

            # Show order history
            st.write("### Order History")
            try:
                order_history = get_client_order_history(selected_client["id"])
                if order_history:
                    for order in order_history:
                        st.json(order)
                else:
                    st.info("No orders found for this client.")
            except Exception as e:
                logger.error(f"Error fetching client order history: {e}")
                st.error(f"Error: {e}")

    # Search Client by Exact Name
    st.subheader("🔍 Search Client by Name")
    with st.form("Search Client Name"):
        search_name = st.text_input("Enter full client name")
        if st.form_submit_button("Search"):
            try:
                results = get_client_by_name(search_name)
                for r in results:
                    st.json(r)
                if not results:
                    st.info("No clients found with that name.")
            except Exception as e:
                logger.error(f"Error searching client by name: {e}")
                st.error(f"Error: {e}")

    # Search Client by Partial Name
    st.subheader("🔍 Search Client by Partial Name")
    with st.form("Search Partial"):
        partial_name = st.text_input("Enter partial name")
        if st.form_submit_button("Search"):
            try:
                results = search_clients_by_partial_name(partial_name)
                for r in results:
                    st.json(r)
                if not results:
                    st.info("No clients found with that partial name.")
            except Exception as e:
                logger.error(f"Error searching client by partial name: {e}")
                st.error(f"Error: {e}")

    # Update Client
    st.subheader("✏️ Update Client Info")
    with st.form("Update Client"):
        client_id = st.text_input("Client ID to update")
        new_name = st.text_input("New Name")
        new_email = st.text_input("New Email")
        new_phone = st.text_input("New Phone")
        if st.form_submit_button("Update"):
            try:
                update_client(client_id, {
                    "name": new_name,
                    "email": new_email,
                    "phone": new_phone
                })
                st.success("Client updated!")
            except Exception as e:
                logger.error(f"Error updating client: {e}")
                st.error(f"Error: {e}")

    # Delete Client
    st.subheader("❌ Delete Client")
    with st.form("Delete Client"):
        delete_id = st.text_input("Client ID to delete")
        if st.form_submit_button("Delete"):
            try:
                delete_client(delete_id)
                st.warning("Client deleted!")
            except Exception as e:
                logger.error(f"Error deleting client: {e}")
                st.error(f"Error: {e}")

    # View Client Order History
    st.subheader("📦 View Client Order History")
    with st.form("Client Orders"):
        order_client_id = st.text_input("Client ID for orders")
        if st.form_submit_button("Show Orders"):
            try:
                orders = get_client_order_history(order_client_id)
                for o in orders:
                    st.json(o)
                if not orders:
                    st.info("No orders found for this client.")
            except Exception as e:
                logger.error(f"Error fetching client orders: {e}")
                st.error(f"Error: {e}")

    # View Client Payments
    st.subheader("💵 View Client Payments")
    with st.form("Client Payments"):
        payment_client_id = st.text_input("Client ID for payments")
        if st.form_submit_button("Show Payments"):
            try:
                payments = get_client_payments(payment_client_id)
                for p in payments:
                    st.json(p)
                if not payments:
                    st.info("No payments found for this client.")
            except Exception as e:
                logger.error(f"Error fetching client payments: {e}")
                st.error(f"Error: {e}")

    # Update Client Due
    st.subheader("💰 Update Client Due")
    with st.form("Update Due"):
        due_client_id = st.text_input("Client ID to update due")
        due_change = st.number_input("Change in due (positive or negative)", step=0.01)
        if st.form_submit_button("Update Due"):
            try:
                update_client_due(due_client_id, due_change)
                st.success("Client due updated.")
            except Exception as e:
                logger.error(f"Error updating client due: {e}")
                st.error(f"Error: {e}")

# ---------------- Suppliers ----------------
with tabs[3]:
    st.header("🏭 Suppliers")

    # Add Supplier Form
    with st.form("Add Supplier"):
        st.subheader("➕ Add New Supplier")
        name = st.text_input("Supplier Name")
        contact_person = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        items = st.text_area("Items Supplied (comma-separated)")
        submitted = st.form_submit_button("Add Supplier")
        if submitted:
            try:
                supplier_data = {
                    "name": name,
                    "contact_person": contact_person,
                    "phone": phone,
                    "items_supplied": [i.strip() for i in items.split(",")],
                    "total_due": 0.0
                }
                add_supplier(supplier_data)
                st.success("✅ Supplier added successfully!")
            except Exception as e:
                logger.error(f"Error adding supplier: {e}")
                st.error(f"Error: {e}")

    # All Suppliers
    st.subheader("📋 All Suppliers")
    try:
        suppliers = get_all_suppliers()
        for supplier in suppliers:
            with st.expander(f"🔍 {supplier['name']}"):
                st.write(supplier)

                # Order History
                st.markdown("**📦 Order History**")
                try:
                    history = get_supplier_order_history(supplier["id"])
                    for order in history:
                        st.json(order)
                    if not history:
                        st.info("No orders found for this supplier.")
                except Exception as e:
                    logger.error(f"Error fetching supplier order history: {e}")
                    st.error(f"Error: {e}")

                # Payment History
                st.markdown("**💵 Payment History**")
                try:
                    payments = get_supplier_payments(supplier["id"])
                    for p in payments:
                        st.json(p)
                    if not payments:
                        st.info("No payments found for this supplier.")
                except Exception as e:
                    logger.error(f"Error fetching supplier payments: {e}")
                    st.error(f"Error: {e}")

                # Update Due
                st.markdown("**➕➖ Update Due Amount**")
                due_change = st.number_input(f"Change due for {supplier['name']}", step=100.0, key=f"due_{supplier['id']}")
                if st.button("Update Due", key=f"update_due_{supplier['id']}"):
                    try:
                        update_supplier_due(supplier["id"], due_change)
                        st.success("✅ Due updated!")
                    except Exception as e:
                        logger.error(f"Error updating supplier due: {e}")
                        st.error(f"Error: {e}")

                # Update Supplier Details
                st.markdown("**✏️ Update Supplier Info**")
                new_name = st.text_input("New Name", supplier["name"], key=f"name_{supplier['id']}")
                if st.button("Update Supplier", key=f"edit_{supplier['id']}"):
                    try:
                        update_supplier(supplier["id"], {"name": new_name})
                        st.success("✅ Supplier info updated!")
                    except Exception as e:
                        logger.error(f"Error updating supplier: {e}")
                        st.error(f"Error: {e}")

                # Delete Supplier
                if st.button("🗑️ Delete Supplier", key=f"delete_{supplier['id']}"):
                    try:
                        delete_supplier(supplier["id"])
                        st.warning("⚠️ Supplier deleted. Refresh the page.")
                    except Exception as e:
                        logger.error(f"Error deleting supplier: {e}")
                        st.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        st.error(f"Error: {e}")

    # Search by Exact Name
    st.subheader("🔍 Search Supplier by Name")
    with st.form("Search Supplier Exact"):
        name_search = st.text_input("Enter exact name")
        if st.form_submit_button("Search"):
            try:
                results = get_supplier_by_name(name_search)
                for r in results:
                    st.json(r)
                if not results:
                    st.info("No suppliers found with that name.")
            except Exception as e:
                logger.error(f"Error searching supplier by name: {e}")
                st.error(f"Error: {e}")

    # Search by Partial Name
    st.subheader("🔎 Search Supplier by Partial Name")
    with st.form("Search Supplier Partial"):
        partial_search = st.text_input("Enter partial name")
        if st.form_submit_button("Search"):
            try:
                results = search_suppliers_by_partial_name(partial_search)
                for r in results:
                    st.json(r)
                if not results:
                    st.info("No suppliers found with that partial name.")
            except Exception as e:
                logger.error(f"Error searching supplier by partial name: {e}")
                st.error(f"Error: {e}")

# ---------------- Invoices ----------------
with tabs[4]:
    st.header("🧾 Invoices")

    # Add Invoice Form
    with st.form("Add Invoice"):
        st.subheader("➕ Add New Invoice")
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
                logger.error(f"Error adding invoice: {e}")
                st.error(f"Error: {e}")

    # All Invoices
    st.subheader("📋 All Invoices")
    try:
        invoices = get_all_invoices()
        for invoice in invoices:
            st.json(invoice)
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        st.error(f"Error: {e}")

    # Search Invoice by Number
    st.subheader("🔍 Search Invoice by Number")
    with st.form("Search Invoice"):
        search_invoice_number = st.text_input("Enter Invoice Number")
        search_submitted = st.form_submit_button("Search")
        if search_submitted:
            try:
                found_invoices = get_invoice_by_number(search_invoice_number)
                if found_invoices:
                    for inv in found_invoices:
                        st.json(inv)
                else:
                    st.info("No invoices found with that number.")
            except Exception as e:
                logger.error(f"Error searching invoice by number: {e}")
                st.error(f"Error: {e}")

    # Update Invoice
    st.subheader("✏️ Update Invoice")
    with st.form("Update Invoice"):
        update_id = st.text_input("Invoice Document ID")
        update_field = st.text_input("Field to Update (e.g., status, total_amount)")
        update_value = st.text_input("New Value")
        update_submitted = st.form_submit_button("Update")
        if update_submitted:
            try:
                update_value_casted = float(update_value) if update_field == "total_amount" else update_value
                update_invoice(update_id, {update_field: update_value_casted})
                st.success("Invoice updated successfully!")
            except Exception as e:
                logger.error(f"Error updating invoice: {e}")
                st.error(f"Error: {e}")

    # Delete Invoice
    st.subheader("🗑️ Delete Invoice")
    with st.form("Delete Invoice"):
        delete_id = st.text_input("Invoice Document ID to Delete")
        delete_submitted = st.form_submit_button("Delete")
        if delete_submitted:
            try:
                delete_invoice(delete_id)
                st.success("Invoice deleted successfully!")
            except Exception as e:
                logger.error(f"Error deleting invoice: {e}")
                st.error(f"Error: {e}")

# ---------------- Finance ----------------
with tabs[5]:
    st.header("💰 Finance Overview")

    # Add Payment
    st.subheader("📥 Record Client Payment")
    with st.form("Add Payment"):
        client_id = st.text_input("Client ID")
        amount = st.number_input("Amount", min_value=0.0)
        invoice_id = st.text_input("Invoice ID (optional)")
        payment_method = st.selectbox("Payment Method", ["cash", "bank transfer", "UPI", "other"])
        notes = st.text_area("Notes", "")
        submitted = st.form_submit_button("Record Payment")
        if submitted:
            try:
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
            except Exception as e:
                logger.error(f"Error adding payment: {e}")
                st.error(f"Error: {e}")

    # Add Expense
    st.subheader("📤 Record Expense")
    with st.form("Add Expense"):
        category = st.selectbox("Category", ["rent", "electricity", "salary", "supplies", "transport", "other"])
        amount = st.number_input("Expense Amount", min_value=0.0, key="expense_amount")
        paid_to = st.text_input("Paid To")
        description = st.text_area("Description")
        submit_expense = st.form_submit_button("Record Expense")
        if submit_expense:
            try:
                from google.cloud import firestore
                add_expense({
                    "category": category,
                    "amount": amount,
                    "date": firestore.SERVER_TIMESTAMP,
                    "paid_to": paid_to,
                    "description": description
                })
                st.success("Expense recorded!")
            except Exception as e:
                logger.error(f"Error adding expense: {e}")
                st.error(f"Error: {e}")

    # View Dues
    st.subheader("📋 Clients with Dues")
    try:
        dues = get_all_dues()
        if dues:
            for d in dues:
                st.markdown(f"**{d['name']}** (Due: ₹{d['total_due']})")
        else:
            st.info("No dues found.")
    except Exception as e:
        logger.error(f"Error fetching dues: {e}")
        st.error(f"Error: {e}")

    # View Payments
    st.subheader("🧾 All Client Payments")
    try:
        payments = get_payments()
        for p in payments:
            st.json(p)
    except Exception as e:
        logger.error(f"Error fetching payments: {e}")
        st.error(f"Error: {e}")

    # View Expenses
    st.subheader("📉 All Expenses")
    try:
        expenses = get_expenses()
        for e in expenses:
            st.json(e)
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        st.error(f"Error: {e}")

    # Finance Summary
    st.subheader("📊 Financial Summary")
    try:
        total_in = get_total_payments()
        total_out = get_total_expenses()
        net = total_in - total_out
        st.markdown(f"""
            - 💸 **Total Payments Received:** ₹{total_in}
            - 📤 **Total Expenses:** ₹{total_out}
            - 💼 **Net Balance:** ₹{net}
        """)
    except Exception as e:
        logger.error(f"Error generating financial summary: {e}")
        st.error(f"Error: {e}")

# ---------------- ChatBot ----------------
with tabs[6]:
    st.header("🤖 Chat with Your AI Business Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Clear chat history
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["user"])
        with st.chat_message("assistant"):
            st.markdown(chat["bot"])

    # Chat input
    user_input = st.chat_input("Ask anything about inventory, orders, finance...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("Thinking..."):
            try:
                logger.debug(f"User input: {user_input}")
                bot_response = run_agent(user_input)
                logger.debug(f"Bot response: {bot_response}")
            except Exception as e:
                logger.error(f"Error running agent: {e}")
                bot_response = f"❌ Error: {e}"
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.chat_history.append({"user": user_input, "bot": bot_response})