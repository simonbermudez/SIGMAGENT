
## Shopify API and Webhook Capabilities

Shopify provides a robust set of APIs and webhooks that allow external applications to interact with store data, including order status and product information. 

**Key Webhooks for Order Status:**
* `orders/create`: Triggered when a new order is placed.
* `orders/updated`: Triggered when an order is updated (e.g., status changes, items added/removed).
* `orders/paid`: Triggered when an order is paid.
* `orders/fulfilled`: Triggered when an order is fulfilled.
* `orders/cancelled`: Triggered when an order is cancelled.

**Key Webhooks for Product Information:**
* `products/create`: Triggered when a new product is created.
* `products/update`: Triggered when a product is updated.
* `products/delete`: Triggered when a product is deleted.

**Relevant API Endpoints:**
* **Order API:** Allows retrieval of order details, updating order status, and managing fulfillments. 
  * Example: `/admin/api/2023-10/orders.json` (to retrieve orders)
* **Product API:** Allows retrieval of product details, updating product information, and managing inventory.
  * Example: `/admin/api/2023-10/products.json` (to retrieve products)

These capabilities will be crucial for the SBDR agent to access real-time order status and product details to answer customer queries effectively.

