# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta
import pytz
from firebase_admin import firestore

def generate_daily_summary():
    db = firestore.client()
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    summary = {
        "orders_placed": 0,
        "total_sales": 0.0,
        "total_purchases": 0.0,
        "items_sold": 0,
        "items_purchased": 0,
        "dues_collected": 0.0,
        "new_clients": 0,
        "new_suppliers": 0,
        "invoices_generated": 0,
        "expenses_logged": 0,
        "total_expenses": 0.0
    }

    # 1. Fetch and summarize orders
    sell_orders = db.collection("Orders").where("type", "==", "sell").where("timestamp", ">=", today).where("timestamp", "<", tomorrow).stream()
    for order in sell_orders:
        data = order.to_dict()
        summary["orders_placed"] += 1
        summary["total_sales"] += data.get("total", 0)
        summary["items_sold"] += sum(item.get("quantity", 0) for item in data.get("items", []))

    purchase_orders = db.collection("Orders").where("type", "==", "purchase").where("timestamp", ">=", today).where("timestamp", "<", tomorrow).stream()
    for order in purchase_orders:
        data = order.to_dict()
        summary["total_purchases"] += data.get("total", 0)
        summary["items_purchased"] += sum(item.get("quantity", 0) for item in data.get("items", []))

    # 2. Fetch dues collected today
    invoices = db.collection("Invoices").where("timestamp", ">=", today).where("timestamp", "<", tomorrow).stream()
    for inv in invoices:
        data = inv.to_dict()
        summary["dues_collected"] += data.get("amount_paid", 0)
        summary["invoices_generated"] += 1

    # 3. Fetch new clients/suppliers added today
    new_clients = db.collection("Clients").where("created_at", ">=", today).where("created_at", "<", tomorrow).stream()
    summary["new_clients"] = len(list(new_clients))

    new_suppliers = db.collection("Suppliers").where("created_at", ">=", today).where("created_at", "<", tomorrow).stream()
    summary["new_suppliers"] = len(list(new_suppliers))

    # 4. Expenses
    expenses = db.collection("Expenses").where("timestamp", ">=", today).where("timestamp", "<", tomorrow).stream()
    for expense in expenses:
        data = expense.to_dict()
        summary["expenses_logged"] += 1
        summary["total_expenses"] += data.get("amount", 0)

    # ✅ Final message
    summary_message = f"""
📋 *Daily Summary - {today.strftime('%d %b %Y')}* 📋

🛒 Orders Placed: {summary['orders_placed']}
💰 Sales: ₹{summary['total_sales']:.2f}
📦 Items Sold: {summary['items_sold']}

🧾 Purchases: ₹{summary['total_purchases']:.2f}
📥 Items Purchased: {summary['items_purchased']}

💸 Dues Collected: ₹{summary['dues_collected']:.2f}
👨‍⚕️ New Clients: {summary['new_clients']}
🚚 New Suppliers: {summary['new_suppliers']}

🧾 Invoices Generated: {summary['invoices_generated']}
💼 Expenses: ₹{summary['total_expenses']:.2f} ({summary['expenses_logged']} entries)
    """.strip()

    return summary_message



# Find these values at https://twilio.com/user/account
# To set up environmental variables, see http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']



client = Client(account_sid, auth_token)

client.api.account.messages.create(
    to="whatsapp:+919201479878",
    from_="whatsapp:+14155238886",
    body="Hello there!")