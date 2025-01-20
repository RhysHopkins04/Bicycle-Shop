from .core import get_connection, create_tables
from .users import (
    initialize_admin, get_current_user_admin_status, get_all_users,
    update_user_details, get_username_by_id, get_user_id_by_username,
    delete_user, promote_user_to_admin, demote_user_from_admin,
    register_user, update_user_password
)
from .products import (
    add_product, update_product, delete_product, list_product,
    get_products, get_product_by_id
)
from .categories import (
    add_category, get_categories, get_category_id, get_category_name,
    update_category, delete_category
)
from .cart import (
    add_to_cart, get_cart_items, update_cart_quantity
)
from .discounts import (
    add_discount, update_discount, toggle_discount_status,
    delete_discount, get_all_discounts, increment_discount_uses,
    verify_discount_qr
)
from .logging import (
    log_user_action, log_admin_action, export_logs_to_temp_file,
    get_dashboard_stats, get_dashboard_alerts
)

__all__ = [
    # Core
    'get_connection', 'create_tables',
    # Users
    'initialize_admin', 'get_current_user_admin_status', 'get_all_users',
    'update_user_details', 'get_username_by_id', 'get_user_id_by_username',
    'delete_user', 'promote_user_to_admin', 'demote_user_from_admin',
    'register_user', 'update_user_password'
    # Products
    'add_product', 'update_product', 'delete_product', 'list_product',
    'get_products', 'get_product_by_id',
    # Categories
    'add_category', 'get_categories', 'get_category_id', 'get_category_name',
    'update_category', 'delete_category',
    # Cart
    'add_to_cart', 'get_cart_items', 'update_cart_quantity',
    # Discounts
    'add_discount', 'update_discount', 'toggle_discount_status',
    'delete_discount', 'get_all_discounts', 'increment_discount_uses',
    'verify_discount_qr',
    # Logging
    'log_user_action', 'log_admin_action', 'export_logs_to_temp_file',
    'get_dashboard_stats', 'get_dashboard_alerts'
]