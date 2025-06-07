
from langchain_core.tools import Tool
from typing import List, Dict
# Import all your Firebase functions
from firebase_config.inventory import *
from firebase_config.clients import *
from firebase_config.finance import *
from firebase_config.invoices import *
from firebase_config.orders import *
from firebase_config.suppliers import *

# Inventory tools
inventory_tools = [
    Tool("GetInventoryItemByName", get_inventory_item_by_name, "Get inventory item details by item name."),
    Tool("SearchInventoryByPartialName", search_inventory_by_partial_name, "Search inventory items by partial item name."),
    Tool("AddInventoryItem", lambda item_data: str(add_inventory_item(item_data)), "Add a new item to the inventory."),
    Tool("UpdateInventoryItem", lambda data: update_inventory_item(data['item_id'], data['updated_fields']) or "Updated", "Update inventory item."),
    Tool("DeleteInventoryItem", lambda item_id: delete_inventory_item(item_id) or "Deleted", "Delete inventory item by ID."),
    Tool("GetAllInventoryItems", lambda _: get_all_inventory_items(), "Get all inventory items."),
    Tool("GetInventoryItemById", get_inventory_item_by_id, "Get inventory item by ID."),
    Tool("GetLowStockItems", lambda _: get_low_stock_items(), "Get items with low stock."),
    Tool("GetItemsByCategory", get_items_by_category, "Get inventory items by category."),
    Tool("GetItemsExpiringSoon", lambda _: get_items_expiring_soon(), "Get inventory items expiring soon."),
]

# Clients tools
client_tools = [
    Tool("GetClientByName", get_client_by_name, "Get client details by client name."),
    Tool("SearchClientsByPartialName", search_clients_by_partial_name, "Search clients by partial name."),
    Tool("AddClient", lambda data: str(add_client(data)), "Add a new client."),
    Tool("UpdateClient", lambda data: update_client(data['client_id'], data['updated_fields']) or "Updated", "Update client."),
    Tool("DeleteClient", lambda client_id: delete_client(client_id) or "Deleted", "Delete client."),
    Tool("GetClientOrderHistory", get_client_order_history, "Get all orders made by a specific client."),
    Tool("GetClientPayments", get_client_payments, "Get payment history of a client."),
    Tool("UpdateClientDue", lambda data: update_client_due(data['client_id'], data['amount']) or "Updated", "Update client's due amount."),
]

# Suppliers tools
supplier_tools = [
    Tool("GetSupplierByName", get_supplier_by_name, "Get supplier details by supplier name."),
    Tool("SearchSuppliersByPartialName", search_suppliers_by_partial_name, "Search suppliers by partial name."),
    Tool("AddSupplier", lambda data: str(add_supplier(data)), "Add a new supplier."),
    Tool("UpdateSupplier", lambda data: update_supplier(data['supplier_id'], data['updated_fields']) or "Updated", "Update supplier."),
    Tool("DeleteSupplier", lambda supplier_id: delete_supplier(supplier_id) or "Deleted", "Delete supplier."),
    Tool("GetSupplierOrderHistory", get_supplier_order_history, "Get order history of a supplier."),
    Tool("GetSupplierPayments", get_supplier_payments, "Get payment history to a supplier."),
    Tool("UpdateSupplierDue", lambda data: update_supplier_due(data['supplier_id'], data['amount']) or "Updated", "Update supplier's due amount."),
    Tool("AddSupplyRecord", lambda data: str(add_supply_record(data)), "Add a new supply record for a supplier."),
]

# Orders tools
order_tools = [
    Tool("GetOrderById", get_order_by_id, "Get order details by order ID."),
    Tool("AddOrder", lambda data: str(add_order(data)), "Add a new order."),
    Tool("UpdateOrder", lambda data: update_order(data['order_id'], data['updated_fields']) or "Updated", "Update order."),
    Tool("DeleteOrder", lambda order_id: delete_order(order_id) or "Deleted", "Delete order."),
    Tool("GetOrdersByClient", get_orders_by_client, "Get orders made by a client."),
    Tool("GetOrdersByDateRange", lambda data: get_orders_by_date_range(data['start_date'], data['end_date']), "Get orders within a date range."),
    Tool("GetOrdersByStatus", get_orders_by_status, "Get orders by status."),
    Tool("GetOrdersBySupplier", get_orders_by_supplier, "Get orders made from a supplier."),
    Tool("GetTotalSalesInPeriod", lambda data: get_total_sales_in_period(data['start_date'], data['end_date']), "Get total sales in a given period."),
    Tool(name="GetAllOrders",func=lambda _: get_all_orders(),description="Get all orders.",return_direct=True),
    Tool("SearchOrdersByInvoiceNumber", search_orders_by_invoice_number, "Search orders by invoice number."),
]

# Invoices tools
invoice_tools = [
    Tool("GetInvoiceByNumber", get_invoice_by_number, "Get invoice details by invoice number."),
    Tool("GetInvoiceById", get_invoice_by_id, "Get invoice details by invoice ID."),
    Tool("AddInvoice", lambda data: str(add_invoice(data)), "Add a new invoice."),
    Tool("UpdateInvoice", lambda data: update_invoice(data['invoice_id'], data['updated_fields']) or "Updated", "Update invoice."),
    Tool("DeleteInvoice", lambda invoice_id: delete_invoice(invoice_id) or "Deleted", "Delete invoice."),
    Tool("GetAllInvoices", lambda _: get_all_invoices(), "Get all invoices."),
]

# Finance tools
finance_tools = [
    Tool("AddExpense", lambda data: str(add_expense(data)), "Add a new expense."),
    Tool("AddPayment", lambda data: str(add_payment(data)), "Add a new payment."),
    Tool("AddSupplierPayment", lambda data: str(add_supplier_payment(data)), "Add a payment to a supplier."),
    Tool("GetAllDues", lambda _: get_all_dues(), "Get all dues."),
    Tool("GetExpenses", lambda _: get_expenses(), "Get all expenses."),
    Tool("GetPayments", lambda _: get_payments(), "Get all payments."),
    Tool("GetSupplierPayments", get_supplier_payments, "Get all payments made to a supplier."),
    Tool("UpdateExpense", lambda data: update_expense(data['expense_id'], data['updated_fields']) or "Updated", "Update an expense."),
    Tool("DeleteExpense", lambda expense_id: delete_expense(expense_id) or "Deleted", "Delete an expense by ID."),
    Tool("GetTotalExpenses", lambda _: get_total_expenses(), "Get total expense amount."),
    Tool("GetTotalPayments", lambda _: get_total_payments(), "Get total payment amount."),
]

# Combine all tools
all_tools = (
    inventory_tools +
    client_tools +
    supplier_tools +
    order_tools +
    invoice_tools +
    finance_tools
)
