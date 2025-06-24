import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import logging
import speech_recognition as sr
os.environ["STREAMLIT_WATCHFILE"] = "false"
import torch
torch._classes = None  # avoid __getattr__ error during reloads

# Add the root of your project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from firebase_config.llama_index_configs import global_settings  # triggers embedding config
from firebase_config.employess import *
from firebase_config.agent import run_agent
from firebase_config.inventory import (
    add_inventory_item, get_all_inventory_items, get_inventory_item_by_name,
    search_inventory_by_partial_name, get_items_by_category, get_low_stock_items,
    get_inventory_item_by_id, update_inventory_item, update_stock_quantity,
    delete_inventory_item, get_items_expiring_soon
)
from firebase_config.dashboard import add_expense, add_payment, add_supplier_payment, get_all_dues, get_date_range, get_expenses, get_inventory_distribution_by_category, get_low_stock_items_dashboard, get_net_profit,  get_order_trend, get_overdue_payments, get_supplier_payments,get_payments, get_total_expenses, get_top_selling_items, get_total_orders, get_total_payments, get_total_revenue 
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
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Business Assistant", layout="wide")

tabs = st.tabs(["Dashboard", "Inventory", "Orders", "Clients", "Suppliers", "Employees", "Finance", "ChatBot"])

# ---------------- Dashboard ----------------
with tabs[0]:
    st.header("📊 Dashboard")

    st.subheader("Overview")
    try:
        # Fetch data for metrics
        total_inventory = len(get_all_inventory_items() or [])
        low_stock_items = get_low_stock_items_dashboard(threshold=10) or []
        total_orders = get_total_orders()
        total_revenue = get_total_revenue()
        total_expenses = get_total_expenses()
        net_profit = get_net_profit()
        total_dues = sum(d['total_due'] for d in get_all_dues() if d.get('total_due', 0.0))

        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Inventory Items", total_inventory)
            st.metric("Low Stock Items", len(low_stock_items))
        with col2:
            st.metric("Total Orders", total_orders)
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        with col3:
            st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
            st.metric("Net Profit", f"₹{net_profit:,.2f}")

        # Inventory by Category Chart
        st.subheader("Inventory by Category")
        try:
            category_dist = get_inventory_distribution_by_category()
            df_category = pd.DataFrame(category_dist)
            st.bar_chart(df_category.set_index("category"))
        except Exception as e:
            logger.error(f"Error generating inventory by category chart: {e}")
            st.error(f"Error: {e}")

        # Sales Over Time (Last 30 Days)
        st.subheader("Sales Over Time (Last 30 Days)")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            sales_trend = get_order_trend(start_date, end_date, group_by="day")
            df_sales = pd.DataFrame(sales_trend)
            df_sales["date"] = pd.to_datetime(df_sales["date"])
            st.line_chart(df_sales.set_index("date"))
        except Exception as e:
            logger.error(f"Error generating sales over time chart: {e}")
            st.error(f"Error: {e}")

        # Low Stock Items Table
        st.subheader("⚠️ Low Stock Items (Threshold: 10)")
        try:
            if low_stock_items:
                df_low_stock = pd.DataFrame(low_stock_items)
                st.dataframe(df_low_stock[["name", "stock_quantity", "category"]])
            else:
                st.info("No low stock items found.")
        except Exception as e:
            logger.error(f"Error fetching low stock items for dashboard: {e}")
            st.error(f"Error: {e}")

        # Top Selling Items
        st.subheader("🏆 Top Selling Items")
        try:
            top_items = get_top_selling_items(limit=5)
            if top_items:
                df_top = pd.DataFrame(top_items)
                st.dataframe(df_top[["item_name", "quantity", "total_amount"]])
            else:
                st.info("No top selling items found.")
        except Exception as e:
            logger.error(f"Error fetching top selling items: {e}")
            st.error(f"Error: {e}")

        # Overdue Payments
        st.subheader("📅 Overdue Payments")
        try:
            overdue_clients = get_overdue_payments(days_overdue=7)
            if overdue_clients:
                df_due = pd.DataFrame(overdue_clients)
                st.dataframe(df_due[["client_name", "total_due", "overdue_days"]])
            else:
                st.info("No overdue payments found.")
        except Exception as e:
            logger.error(f"Error fetching overdue payments: {e}")
            st.error(f"Error: {e}")

        # Quick Links
        st.subheader("🔗 Quick Actions")
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("Manage Inventory"):
                st.switch_page("Inventory")
            if st.button("View Orders"):
                st.switch_page("Orders")
        with col5:
            if st.button("Manage Clients"):
                st.switch_page("Clients")
            if st.button("View Suppliers"):
                st.switch_page("Suppliers")
        with col6:
            if st.button("Manage Invoices"):
                st.switch_page("Invoices")
            if st.button("View Finance"):
                st.switch_page("Finance")

    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        st.error(f"Error: {e}")

# ---------------- Inventory ----------------
with tabs[1]:
    st.header("📦 Inventory Management")

    # 1. Add New Inventory Item
    st.subheader("➕ Add New Inventory Item")
    with st.form("Add Inventory"):
        name = st.text_input("Item Name")
        category = st.selectbox("Category", [
            "blood tubing", "chemical", "CITOS", "dialysers", "diasafe",
            "machine", "needle", "other item", "spare", "surgical"
        ])
        low_stock_threshold = st.number_input("Low Stock Threshold", min_value=0.0, value=10.0)
        unit_price = st.number_input("Unit Price", min_value=0.0)

        submitted = st.form_submit_button("Add Item")
        if submitted:
            try:
                # You can generate item_id here like "I0001" if needed
                add_inventory_item({
                    "name": name,
                    "category": category,
                    "low_stock": low_stock_threshold,
                    "unit_price": unit_price,
                    "stock_quantity": 0,
                    "batches": []
                })
                st.success("✅ Inventory item added (waiting for stock via orders)")
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
with tabs[2]:
    st.header("📄 Orders")

    # Add Order Section
    st.subheader("➕ Add Order")
    with st.form("Add Order Form"):

        # Order Type
        order_type = st.radio("Order Type", ["purchase", "sales", "delivery_challan"])

        # Client or Supplier Info based on order type
        client_id = client_name = supplier_id = supplier_name = ""

        if order_type in ["sales", "delivery_challan"]:
            client_name = st.text_input("Client Name")
            client_id = st.text_input("Client ID (auto-filled by UI)")
        elif order_type == "purchase":
            supplier_name = st.text_input("Supplier Name")
            supplier_id = st.text_input("Supplier ID (auto-filled by UI)")

        # Items Section
        num_items = st.number_input("Number of Items", min_value=1, value=1, step=1)
        items = []

        st.markdown("### 📦 Items")
        for i in range(num_items):
            with st.expander(f"🧾 Item {i+1}", expanded=True):
                item_name = st.text_input("Item Name", key=f"item_name_{i}")
                quantity = st.number_input("Quantity", min_value=1, key=f"qty_{i}")
                price = st.number_input("Price (₹)", min_value=0.0, key=f"price_{i}")
                tax = st.number_input("Tax (%)", min_value=0.0, key=f"tax_{i}")
                batch_number = st.text_input("Batch Number", key=f"batch_{i}")
                expiry = st.text_input("Expiry (MM/YYYY)", key=f"expiry_{i}")

                items.append({
                    "item_name": item_name.strip(),
                    "quantity": quantity,
                    "price": price,
                    "tax": tax,
                    "batch_number": batch_number,
                    "expiry": expiry
                })

        # Invoice / Challan
        st.markdown("### 📄 Invoice / Challan Info")
        invoice_number = challan_number = None
        if order_type == "delivery_challan":
            challan_number = st.text_input("Challan Number")
        else:
            invoice_number = st.text_input("Invoice Number")

        # Payment Info
        st.markdown("### 💰 Payment Details")
        total_amount = st.number_input("Total Amount (₹)", min_value=0.0)
        amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0)
        payment_method = st.selectbox("Payment Method", ["cash", "UPI", "bank", "unpaid"])
        payment_status = st.selectbox("Payment Status", ["unpaid", "partial", "paid"])

        # Order Meta
        status = st.selectbox("Order Status", ["pending", "completed"])
        remarks = st.text_area("Remarks")

        # Admin Info
        st.markdown("### 🧑‍💻 Admin Info")
        draft = st.checkbox("Is Draft?", value=False)
        updated_by = st.text_input("Updated By", value="admin")
        created_by = st.text_input("Created By", value="admin")
        amount_collected_by = st.text_input("Amount Collected By", value="")

        submitted = st.form_submit_button("Submit Order")

        if submitted:
            try:
                # 🔍 Validation
                if order_type in ["sales", "delivery_challan"]:
                    if not client_id or not client_name:
                        st.error("❌ Client ID and Name are required for sales/delivery orders.")
                        st.stop()
                elif order_type == "purchase":
                    if not supplier_id or not supplier_name:
                        st.error("❌ Supplier ID and Name are required for purchase orders.")
                        st.stop()

                for idx, item in enumerate(items):
                    if not item["item_name"]:
                        st.error(f"❌ Item #{idx+1} is missing a name.")
                        st.stop()

                # ✅ Construct Order Data
                order_data = {
                    "order_type": order_type,
                    "status": status,
                    "items": items,
                    "total_amount": total_amount,
                    "invoice_number": invoice_number,
                    "challan_number": challan_number,
                    "payment_method": payment_method,
                    "amount_paid": amount_paid,
                    "payment_status": payment_status,
                    "remarks": remarks,
                    "draft": draft,
                    "updated_by": updated_by,
                    "created_by": created_by,
                    "amount_collected_by": amount_collected_by
                }

                if order_type in ["sales", "delivery_challan"]:
                    order_data["client_id"] = client_id
                    order_data["client_name"] = client_name
                if order_type == "purchase":
                    order_data["supplier_id"] = supplier_id
                    order_data["supplier_name"] = supplier_name

                # 📝 Add Order to Firestore
                order_id = add_order(order_data)
                st.success(f"✅ Order added successfully! ID: {order_id}")

            except Exception as e:
                logger.error(f"[❌] Error adding order: {e}")
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
with tabs[3]:
    st.header("👥 Clients")

    # Add Client Form
    with st.form("Add Client"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Client Name")
            client_id = st.text_input("Client ID (e.g., C0001)")
            pan = st.text_input("PAN")
            gst = st.text_input("GST")
        with col2:
            poc_name = st.text_input("POC Name (Contact Person)")
            poc_contact = st.text_input("POC Contact")
            address = st.text_area("Address")

        submitted = st.form_submit_button("Add Client")

        if submitted:
            try:
                add_client({
                    "id": client_id,
                    "name": name,
                    "PAN": pan,
                    "GST": gst,
                    "POC_name": poc_name,
                    "POC_contact": poc_contact,
                    "due_amount": 0.0,
                    "address": address
                })
                st.success(f"✅ Client '{name}' added with ID: {client_id}")
            except Exception as e:
                logger.error(f"Error adding client: {e}")
                st.error(f"❌ Error: {e}")


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
with tabs[4]:
    st.header("🏭 Suppliers")

    # Add Supplier Form
    with st.form("Add Supplier"):
        st.subheader("➕ Add New Supplier")
        col1, col2 = st.columns(2)
        with col1:
            supplier_id = st.text_input("Supplier ID (e.g., S0001)")
            name = st.text_input("Supplier Name")
            contact = st.text_input("Contact Number")
        with col2:
            address = st.text_area("Supplier Address")

        submitted = st.form_submit_button("Add Supplier")

        if submitted:
            try:
                supplier_data = {
                    "id": supplier_id,
                    "name": name,
                    "contact": contact,
                    "due": 0.0,
                    "address": address
                }
                add_supplier(supplier_data)
                st.success(f"✅ Supplier '{name}' added with ID: {supplier_id}")
            except Exception as e:
                logger.error(f"Error adding supplier: {e}")
                st.error(f"❌ Error: {e}")


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
with tabs[5]:
    st.header("👨‍💼 Employees")

    # Add Employee Form
    with st.form("Add Employee"):
        st.subheader("➕ Add New Employee")
        col1, col2 = st.columns(2)
        with col1:
            employee_id = st.text_input("Employee ID (e.g., E0001)")
            name = st.text_input("Employee Name")
        with col2:
            collected = st.number_input("Initial Amount Collected", min_value=0.0)
            paid = st.number_input("Initial Amount Paid", min_value=0.0)

        submitted = st.form_submit_button("Add Employee")

        if submitted:
            try:
                employee_data = {
                    "id": employee_id,
                    "name": name,
                    "collected": collected,
                    "paid": paid
                }
                add_employee(employee_data)
                st.success(f"✅ Employee '{name}' added with ID: {employee_id}")
            except Exception as e:
                logger.error(f"Error adding employee: {e}")
                st.error(f"❌ Error: {e}")


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
with tabs[6]:
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
        paid_by = st.text_input("Paid By (e.g., Employee Name or ID)")
        remarks = st.text_area("Remarks / Description")

        submit_expense = st.form_submit_button("Record Expense")

        if submit_expense:
            try:
                from google.cloud import firestore
                add_expense({
                    "amount": amount,
                    "category": category,
                    "paid_by": paid_by,
                    "remarks": remarks,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP
                })
                st.success("✅ Expense recorded successfully!")
            except Exception as e:
                logger.error(f"Error adding expense: {e}")
                st.error(f"❌ Error: {e}")


    # View Dues
    st.subheader("📋 Clients with Dues")
    try:
        dues = get_all_dues()
        if dues:
            for d in dues:
                st.markdown(f"**{d['name']}**: ₹{d['total_due']}")
        else:
            st.info("No dues found.")
    except Exception as e:
        logger.error(f"Error fetching dues: {e}")
        st.error(f"Error: {e}")

    # View Payments
    st.subheader("🧾 All Payments")
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
        total_payments = get_total_payments()
        total_expenses = get_total_expenses()
        net = total_payments - total_expenses
        st.markdown(f"""
            - 💸 **Total Payments Received**: ₹{total_payments}
            - 📤 **Total Expenses**: ₹{total_expenses}
            - 💰 **Net Balance**: ₹{net}
        """
        )
    except Exception as e:
        logger.error(f"Error generating financial summary: {e}")
        st.error(f"Error: {e}")

# --------------------------- ChatBot ------------------
with tabs[7]:
    st.header("🤖 Contact Form")

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
                bot_response = f"Error: {e}"
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.chat_history.append({"user": user_input, "bot": bot_response})

    # 1. Voice Input Button
    st.subheader("🎤 Voice Input")
    if st.button("Start Listening"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            audio = recognizer.listen(source)
            st.success("Audio captured!")

            try:
                text = recognizer.recognize_google(audio)
                st.success(f"Recognized: {text}")

                st.info("Querying agent...")
                response = run_agent(text)
                st.success(f"💬 Agent: {response}")
            except sr.UnknownValueError:
                st.error("Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Request failed: {e}")
