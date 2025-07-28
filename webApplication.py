import http.server
import socketserver
import urllib.parse
import json
import os

# --- Configuration ---
PORT = 8000 # Port to run the web server on

# Product data - this would typically come from a database
products_data_json = """
[
  { "id": 1, "name": "Laptop Pro", "category": "Electronics", "price": 1200.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Laptop" },
  { "id": 2, "name": "Mechanical Keyboard", "category": "Electronics", "price": 150.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Keyboard" },
  { "id": 3, "name": "Wireless Mouse", "category": "Electronics", "price": 50.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Mouse" },
  { "id": 4, "name": "Smartphone X", "category": "Electronics", "price": 800.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Phone" },
  { "id": 5, "name": "Designer T-Shirt", "category": "Apparel", "price": 30.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=T-Shirt" },
  { "id": 6, "name": "Denim Jeans", "category": "Apparel", "price": 60.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Jeans" },
  { "id": 7, "name": "Running Shoes", "category": "Footwear", "price": 90.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Shoes" },
  { "id": 8, "name": "Leather Boots", "category": "Footwear", "price": 120.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Boots" },
  { "id": 9, "name": "Fantasy Novel", "category": "Books", "price": 25.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Book" },
  { "id": 10, "name": "Cooking Guide", "category": "Books", "price": 20.00, "image": "https://placehold.co/150x150/F0F8FF/000000?text=Cookbook" }
]
"""
PRODUCTS = json.loads(products_data_json)

# Get unique categories from the product data
CATEGORIES = ['All'] + sorted(list(set(product['category'] for product in PRODUCTS)))

# Global shopping cart (shared by all users in this simple example)
# In a real app, this would be per-user session data
shopping_cart = []

class MyHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler to serve the product display web application.
    """
    def do_GET(self):
        """
        Handles GET requests for the web application.
        Parses URLs to display products, add to cart, or remove from cart.
        """
        global shopping_cart # Declare global here, at the start of the method

        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        current_category = query_params.get('category', ['All'])[0]
        redirect_path = '/' # Default redirect path

        if path == '/add_to_cart':
            product_id = int(query_params.get('product_id', [0])[0])
            product_to_add = next((p for p in PRODUCTS if p['id'] == product_id), None)
            if product_to_add:
                found = False
                for item in shopping_cart:
                    if item['id'] == product_id:
                        item['quantity'] += 1
                        found = True
                        break
                if not found:
                    shopping_cart.append({
                        'id': product_to_add['id'],
                        'name': product_to_add['name'],
                        'price': product_to_add['price'],
                        'image': product_to_add['image'],
                        'quantity': 1
                    })
            # Redirect back to the product list, preserving the category
            redirect_path = f"/?category={current_category}"
            self.send_response(302) # Found (redirect)
            self.send_header('Location', redirect_path)
            self.end_headers()
            return

        elif path == '/remove_from_cart':
            product_id = int(query_params.get('product_id', [0])[0])
            new_cart = []
            for item in shopping_cart:
                if item['id'] == product_id:
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                        new_cart.append(item)
                else:
                    new_cart.append(item)
            shopping_cart = new_cart # Update the global cart
            # Redirect back to the product list, preserving the category
            redirect_path = f"/?category={current_category}"
            self.send_response(302) # Found (redirect)
            self.send_header('Location', redirect_path)
            self.end_headers()
            return

        # Handle serving the main page
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Filter products based on selected category
        filtered_products = []
        if current_category == 'All':
            filtered_products = PRODUCTS
        else:
            filtered_products = [p for p in PRODUCTS if p['category'] == current_category]

        # Calculate cart total
        cart_total = sum(item['price'] * item['quantity'] for item in shopping_cart)

        # Generate HTML content
        html_content = self._generate_html(filtered_products, CATEGORIES, current_category, shopping_cart, cart_total)
        self.wfile.write(html_content.encode('utf-8'))

    def _generate_html(self, products, categories, selected_category, cart, cart_total):
        """
        Generates the full HTML page content.
        This replaces the Jinja2 templating from the Flask example.
        """
        # --- Start HTML Structure ---
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Python Online Store</title>
    <style>
        /* Basic Tailwind-like classes for styling */
        body {{
            font-family: 'Inter', sans-serif;
            margin: 0;
            background-color: #f3f4f6; /* gray-100 */
            color: #1f2937; /* gray-900 */
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem; /* p-6 */
        }}
        .header {{
            background-color: #4f46e5; /* indigo-700 */
            color: white;
            padding: 1rem; /* p-4 */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* shadow-md */
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            font-size: 1.5rem; /* text-2xl */
            font-weight: bold;
        }}
        .relative {{
            position: relative;
        }}
        .absolute {{
            position: absolute;
        }}
        .-top-2 {{ top: -0.5rem; }}
        .-right-2 {{ right: -0.5rem; }}
        .bg-red-500 {{ background-color: #ef4444; }}
        .text-white {{ color: white; }}
        .text-xs {{ font-size: 0.75rem; }}
        .font-bold {{ font-weight: bold; }}
        .rounded-full {{ border-radius: 9999px; }}
        .h-5 {{ height: 1.25rem; }}
        .w-5 {{ width: 1.25rem; }}
        .flex {{ display: flex; }}
        .items-center {{ align-items: center; }}
        .justify-center {{ justify-content: center; }}
        .grid {{ display: grid; }}
        .grid-cols-1 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }}
        .lg\\:grid-cols-4 {{ /* Escaped colon for CSS class name */
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }}
        .gap-6 {{ gap: 1.5rem; }}
        .bg-white {{ background-color: white; }}
        .rounded-lg {{ border-radius: 0.5rem; }}
        .shadow-md {{ box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); }}
        .p-6 {{ padding: 1.5rem; }}
        .h-fit {{ height: fit-content; }}
        .sticky {{ position: sticky; }}
        .top-4 {{ top: 1rem; }}
        .text-xl {{ font-size: 1.25rem; }}
        .mb-4 {{ margin-bottom: 1rem; }}
        .text-gray-800 {{ color: #1f2937; }}
        .space-y-2 > *:not([hidden]) ~ *:not([hidden]) {{ margin-top: 0.5rem; }}
        .block {{ display: block; }}
        .w-full {{ width: 100%; }}
        .text-left {{ text-align: left; }}
        .px-4 {{ padding-left: 1rem; padding-right: 1rem; }}
        .py-2 {{ padding-top: 0.5rem; padding-bottom: 0.5rem; }}
        .rounded-md {{ border-radius: 0.375rem; }}
        .transition-colors {{ transition-property: background-color, border-color, color, fill, stroke; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}
        .duration-200 {{ transition-duration: 200ms; }}
        .bg-indigo-100 {{ background-color: #e0e7ff; }}
        .text-indigo-700 {{ color: #4338ca; }}
        .font-semibold {{ font-weight: 600; }}
        .text-gray-700 {{ color: #374151; }}
        .hover\\:bg-gray-100:hover {{ background-color: #f3f4f6; }}
        .text-2xl {{ font-size: 1.5rem; }}
        .mb-6 {{ margin-bottom: 1.5rem; }}
        .sm\\:grid-cols-2 {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
        .md\\:grid-cols-2 {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
        .lg\\:grid-cols-2 {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
        .xl\\:grid-cols-3 {{
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }}
        .p-4 {{ padding: 1rem; }}
        .flex-col {{ flex-direction: column; }}
        .items-center {{ align-items: center; }}
        .justify-between {{ justify-content: space-between; }}
        .transform {{ transform: var(--tw-transform); }}
        .transition-transform {{ transition-property: transform; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}
        .hover\\:scale-105:hover {{ transform: scale(1.05); }}
        .w-32 {{ width: 8rem; }}
        .h-32 {{ height: 8rem; }}
        .object-cover {{ object-fit: cover; }}
        .mb-4 {{ margin-bottom: 1rem; }}
        .text-lg {{ font-size: 1.125rem; }}
        .text-center {{ text-align: center; }}
        .text-sm {{ font-size: 0.875rem; }}
        .text-gray-600 {{ color: #4b5563; }}
        .mb-2 {{ margin-bottom: 0.5rem; }}
        .text-indigo-600 {{ color: #4f46e5; }}
        .bg-indigo-500 {{ background-color: #6366f1; }}
        .hover\\:bg-indigo-600:hover {{ background-color: #4f46e5; }}
        .focus\\:outline-none:focus {{ outline: 2px solid transparent; outline-offset: 2px; }}
        .focus\\:ring-2:focus {{ box-shadow: 0 0 0 2px var(--tw-ring-color); }}
        .focus\\:ring-indigo-500:focus {{ --tw-ring-color: #6366f1; }}
        .focus\\:ring-opacity-50:focus {{ --tw-ring-opacity: 0.5; }}
        .bg-gray-50 {{ background-color: #f9fafb; }}
        .p-3 {{ padding: 0.75rem; }}
        .shadow-sm {{ box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }}
        .mb-2 {{ margin-bottom: 0.5rem; }}
        .w-12 {{ width: 3rem; }}
        .h-12 {{ height: 3rem; }}
        .mr-3 {{ margin-right: 0.75rem; }}
        .font-medium {{ font-weight: 500; }}
        .bg-red-500 {{ background-color: #ef4444; }}
        .px-3 {{ padding-left: 0.75rem; padding-right: 0.75rem; }}
        .py-1 {{ padding-top: 0.25rem; padding-bottom: 0.25rem; }}
        .hover\\:bg-red-600:hover {{ background-color: #dc2626; }}
        .text-gray-500 {{ color: #6b7280; }}
        .space-y-3 > *:not([hidden]) ~ *:not([hidden]) {{ margin-top: 0.75rem; }}
        .max-h-80 {{ max-height: 20rem; }}
        .overflow-y-auto {{ overflow-y: auto; }}
        .pr-2 {{ padding-right: 0.5rem; }}
        .border-t {{ border-top-width: 1px; border-color: #e5e7eb; /* gray-200 */ }}
        .pt-4 {{ padding-top: 1rem; }}
        .mt-4 {{ margin-top: 1rem; }}
        .bg-green-500 {{ background-color: #22c55e; }}
        .hover\\:bg-green-600:hover {{ background-color: #16a34a; }}
        .focus\\:ring-green-500:focus {{ --tw-ring-color: #22c55e; }}

        /* Custom scrollbar for cart */
        .overflow-y-auto::-webkit-scrollbar {{
            width: 8px;
        }}
        .overflow-y-auto::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}
        .overflow-y-auto::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 10px;
        }}
        .overflow-y-auto::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}

        /* Responsive adjustments */
        @media (min-width: 1024px) {{ /* lg breakpoint */
            .lg\\:col-span-1 {{ grid-column: span 1 / span 1; }}
            .lg\\:col-span-2 {{ grid-column: span 2 / span 2; }}
            .lg\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (min-width: 640px) {{ /* sm breakpoint */
            .sm\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (min-width: 768px) {{ /* md breakpoint */
            .md\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (min-width: 1280px) {{ /* xl breakpoint */
            .xl\\:grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        }}
    </style>
</head>
<body>
    <div class="min-h-screen bg-gray-100 font-sans text-gray-900">
        <!-- Header -->
        <header class="header">
            <div class="container flex justify-between items-center">
                <h1>My Online Store</h1>
                <div class="relative">
                    <!-- Cart Icon SVG -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    {len(cart) > 0 and f"""
                        <span class="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                            {len(cart)}
                        </span>
                    """ or ""}
                </div>
            </div>
        </header>

        <div class="container grid grid-cols-1 lg:grid-cols-4 gap-6">
            <!-- Category Filter Section -->
            <aside class="lg:col-span-1 bg-white rounded-lg shadow-md p-6 h-fit sticky top-4">
                <h2 class="text-xl font-bold mb-4 text-gray-800">Categories</h2>
                <ul class="space-y-2">
                    {"".join([f"""
                    <li>
                        <a href="/?category={cat}"
                           class="block w-full text-left px-4 py-2 rounded-md transition-colors duration-200
                                  { 'bg-indigo-100 text-indigo-700 font-semibold' if selected_category == cat else 'text-gray-700 hover:bg-gray-100' }">
                            {cat}
                        </a>
                    </li>
                    """ for cat in categories])}
                </ul>
            </aside>

            <!-- Products Display Section -->
            <main class="lg:col-span-2">
                <h2 class="text-2xl font-bold mb-6 text-gray-800">Products</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                    {"".join([f"""
                    <div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-center justify-between transform transition-transform duration-200 hover:scale-105">
                        <img src="{product['image']}" alt="{product['name']}" class="w-32 h-32 object-cover rounded-md mb-4"
                             onerror="this.onerror=null;this.src='https://placehold.co/150x150/F0F8FF/000000?text=No+Image';">
                        <h3 class="text-lg font-semibold text-gray-800 text-center">{product['name']}</h3>
                        <p class="text-sm text-gray-600 mb-2">{product['category']}</p>
                        <p class="text-xl font-bold text-indigo-600 mb-4">${product['price']:.2f}</p>
                        <a href="/add_to_cart?product_id={product['id']}&category={selected_category}"
                           class="bg-indigo-500 text-white px-4 py-2 rounded-full hover:bg-indigo-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
                            Add to Cart
                        </a>
                    </div>
                    """ for product in products])}
                </div>
            </main>

            <!-- Shopping Cart Section -->
            <aside class="lg:col-span-1 bg-white rounded-lg shadow-md p-6 h-fit sticky top-4">
                <h2 class="text-xl font-bold mb-4 text-gray-800 flex items-center justify-between">
                    Shopping Cart
                    <!-- Cart Icon SVG -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                </h2>
                {f"""
                { 'Your cart is empty.' if len(cart) == 0 else '' }
                """}
                {f"""
                { "" if len(cart) == 0 else f'''
                    <div class="space-y-3 mb-4 max-h-80 overflow-y-auto pr-2">
                        {"".join([f"""
                        <div class="flex items-center justify-between bg-gray-50 p-3 rounded-md shadow-sm mb-2">
                            <div class="flex items-center">
                                <img src="{item['image']}" alt="{item['name']}" class="w-12 h-12 object-cover rounded-md mr-3"
                                     onerror="this.onerror=null;this.src='https://placehold.co/50x50/F0F8FF/000000?text=No+Image';">
                                <div>
                                    <h4 class="font-medium text-gray-800">{item['name']}</h4>
                                    <p class="text-sm text-gray-600">Qty: {item['quantity']}</p>
                                </div>
                            </div>
                            <div class="flex items-center">
                                <p class="font-semibold text-indigo-600 mr-3">${item['price'] * item['quantity']:.2f}</p>
                                <a href="/remove_from_cart?product_id={item['id']}&category={selected_category}"
                                   class="bg-red-500 text-white px-3 py-1 rounded-full text-sm hover:bg-red-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50">
                                    Remove
                                </a>
                            </div>
                        </div>
                        """ for item in cart])}
                    </div>
                    <div class="border-t pt-4 mt-4">
                        <div class="flex justify-between items-center font-bold text-lg text-gray-800">
                            <span>Total:</span>
                            <span>${cart_total:.2f}</span>
                        </div>
                        <button class="mt-4 w-full bg-green-500 text-white px-4 py-2 rounded-full hover:bg-green-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50">
                            Proceed to Checkout
                        </button>
                    </div>
                ''' }
                """}
            </aside>
        </div>
    </div>
</body>
</html>
"""
        return html


# --- Main Server Setup ---
def run_server():
    """Starts the HTTP server."""
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()