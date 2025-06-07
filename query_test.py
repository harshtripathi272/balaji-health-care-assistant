from firebase_config.llama_index_configs.order_index import load_orders_index

orders_index = load_orders_index()
response = orders_index.as_query_engine().query("show me all orders")
print(response.response)
