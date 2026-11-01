import pandas as pd
import os

os.makedirs("data/cleaned", exist_ok=True)

orders = pd.read_csv("data/raw/olist_orders_dataset.csv")
print(orders.shape)
print(orders.isnull().sum())

for col in ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date","order_delivered_customer_date", "order_estimated_delivery_date"]:orders[col] = pd.to_datetime(orders[col])

print("duplicate orders:", orders["order_id"].duplicated().sum())
orders = orders.drop_duplicates(subset="order_id")

print(orders["order_purchase_timestamp"].dt.to_period("M").value_counts().sort_index())
orders = orders[(orders["order_purchase_timestamp"] >= "2017-01-01") &(orders["order_purchase_timestamp"] < "2018-09-01")]
print("orders after date filter:", len(orders))

items = pd.read_csv("data/raw/olist_order_items_dataset.csv")
items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"])
items = items[items["order_id"].isin(orders["order_id"])]

payments = pd.read_csv("data/raw/olist_order_payments_dataset.csv")
payments = payments[payments["order_id"].isin(orders["order_id"])]
print(payments["payment_type"].value_counts())
payments = payments[payments["payment_type"] != "not_defined"]

reviews = pd.read_csv("data/raw/olist_order_reviews_dataset.csv")
reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"])
reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"])
print("orders with repeated reviews:", reviews["order_id"].duplicated().sum())
reviews = reviews.sort_values("review_answer_timestamp")
reviews = reviews.drop_duplicates(subset="order_id", keep="last")
reviews = reviews[reviews["order_id"].isin(orders["order_id"])]
reviews = reviews.drop(columns=["review_comment_title", "review_comment_message"])

products = pd.read_csv("data/raw/olist_products_dataset.csv")
products = products.rename(columns={"product_name_lenght": "product_name_length","product_description_lenght": "product_description_length"})
translation = pd.read_csv("data/raw/product_category_name_translation.csv")

translation.loc[len(translation)] = ["pc_gamer", "pc_gamer"]
translation.loc[len(translation)] = ["portateis_cozinha_e_preparadores_de_alimentos","portable_kitchen_food_preparers"]

products = products.merge(translation, on="product_category_name", how="left")
print("products with no category:", products["product_category_name_english"].isnull().sum())
products["category"] = products["product_category_name_english"].fillna("unknown")
products["category"] = products["category"].str.replace("_", " ").str.title()
products = products.drop(columns=["product_category_name", "product_category_name_english"])

customers = pd.read_csv("data/raw/olist_customers_dataset.csv")
sellers = pd.read_csv("data/raw/olist_sellers_dataset.csv")
customers["customer_city"] = customers["customer_city"].str.title()
sellers["seller_city"] = sellers["seller_city"].str.title()

geo = pd.read_csv("data/raw/olist_geolocation_dataset.csv")
print("geolocation rows:", len(geo))
geo = geo.groupby("geolocation_zip_code_prefix").agg(lat=("geolocation_lat", "mean"),lng=("geolocation_lng", "mean")).reset_index()
print("geolocation rows after grouping by zip:", len(geo))

orders.to_csv("data/cleaned/orders_clean.csv", index=False)
items.to_csv("data/cleaned/order_items_clean.csv", index=False)
payments.to_csv("data/cleaned/payments_clean.csv", index=False)
reviews.to_csv("data/cleaned/reviews_clean.csv", index=False)
products.to_csv("data/cleaned/products_clean.csv", index=False)
customers.to_csv("data/cleaned/customers_clean.csv", index=False)
sellers.to_csv("data/cleaned/sellers_clean.csv", index=False)
geo.to_csv("data/cleaned/geolocation_clean.csv", index=False)
print("done")