# Packer App - Complete Implementation Guide

A production-ready FastAPI-based Picker/Packer Application with complete integration to Order Service and Inventory Management System.

## 🎯 Features

✅ **Order Management** - Receive orders via webhook from order app  
✅ **Product Sync** - Automatic product creation and updates  
✅ **Inventory Management** - Track stock levels by store  
✅ **Picking Workflow** - QR scan, weighing machine, or manual entry  
✅ **Order Packing** - Complete and ship orders  
✅ **Service Integration** - Bi-directional communication with order service  
✅ **JWT Authentication** - Secure picker agent authentication  
✅ **Responsive UI** - Complete web interface for agents  
✅ **Comprehensive Testing** - HTTP tests and test suites  

---

## 📁 Project Structure

```
packer_app/
├── models/                          # Database models and CRUD operations
│   ├── __init__.py                 # Models export
│   ├── database.py                 # Database configuration & session
│   ├── product.py                  # Product model & CRUD
│   ├── inventory.py                # Inventory model & CRUD
│   ├── customer.py                 # Customer model & CRUD
│   ├── order.py                    # Order & OrderItem models & CRUD
│   ├── picking.py                  # PickingActivity & CrateLabel models & CRUD
│   └── agent.py                    # Agent model & CRUD
│
├── controllers/                     # API route handlers
│   ├── __init__.py
│   ├── agents.py                   # Agent management & authentication
│   ├── orders.py                   # Order endpoints
│   ├── picking.py                  # Picking workflow
│   ├── products.py                 # Product endpoints
│   ├── webhooks.py                 # Webhook handling
│   └── schemas.py                  # Pydantic schemas for all models
│
├── services/                        # External service clients
│   ├── __init__.py
│   ├── order_client.py             # Order service client
│   ├── inventory_client.py         # Inventory service client
│   ├── customer_client.py          # Customer service client
│   ├── order_service.py            # Order business logic
│   ├── inventory_service.py        # Inventory business logic
│   └── customer_service.py         # Customer business logic
│
├── utils/                           # Utility functions
│   ├── auth.py                     # JWT & authentication utilities
│   └── helpers.py                  # Helper functions
│
├── frontend/                        # Frontend assets
│   ├── static/                     # Static files (CSS, JS, images)
│   └── templates/                  # HTML templates
│       ├── index.html              # Main UI (login & dashboard)
│       └── ...
│
├── main.py                          # FastAPI app initialization
├── config.py                        # Configuration management
├── .env                             # Environment variables
├── requirements.txt                 # Python dependencies
├── test_main.http                   # API test cases
├── README.md                        # This file
└── picker_app.db                    # SQLite database
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create/update `.env` file:
```env
# Database
DATABASE_URL=sqlite:///picker_app.db

# Server
ORDER_SERVICE_HOST=http://localhost:8000
ORDER_SERVICE_USER_ID=1
ORGANIZATION_ID=5

# Security
SECRET_KEY=your_very_secure_secret_key_change_this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Mode
DEBUG=True
```

For PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/picker_db
```

### 3. Start the Application
```bash
python main.py
```

The app will start on: **http://localhost:8000**

### 4. Access the Application
- **UI (Dashboard)**: http://localhost:8000/ui
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📋 API Endpoints

### Authentication
- `POST /api/v1/agents/register` - Register new agent
- `POST /api/v1/agents/login` - Login agent (returns JWT token)
- `GET /api/v1/agents/me` - Get current agent info (requires auth)

### Products
- `POST /api/v1/products` - Create/update product
- `GET /api/v1/products` - List all products (paginated)
- `GET /api/v1/products/{product_id}` - Get product details

### Inventory
- `POST /api/v1/inventory` - Create/update inventory
- `GET /api/v1/inventory/{product_id}/{store_id}` - Get inventory details

### Orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - List all orders (paginated)
- `GET /api/v1/orders/{order_id}` - Get order details
- `GET /api/v1/orders/reference/{reference_number}` - Get order by reference
- `PATCH /api/v1/orders/{order_id}/status` - Update order status
- `PATCH /api/v1/orders/{order_id}/picking-status` - Update picking status

### Picking & Packing
- `POST /api/v1/picking/add-item` - Add item to order
- `POST /api/v1/picking/complete` - Complete picking and pack order
- `POST /api/v1/picking/crate-label` - Create crate label

### Webhooks
- `POST /webhook/order` - Receive new order from order service

### Health
- `GET /health` - Health check
- `GET /` - App info

---

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:

1. **Register** a new agent:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agent1",
    "password": "securepassword",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210"
  }'
```

2. **Login** to get access token:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=agent1&password=securepassword"
```

3. **Use token** in protected endpoints:
```bash
curl -X GET "http://localhost:8000/api/v1/agents/me" \
  -H "Authorization: Bearer <your_access_token>"
```

---

## 📊 Database Models

### Product
- `id`: Primary key
- `product_id`: External product ID
- `name`: Product name
- `slug`: URL-friendly name
- `images`: JSON array of images
- `status`: ENABLED/DISABLED
- `created_at`, `updated_at`: Timestamps

### Inventory
- `id`: Primary key
- `product_id`: FK to Product
- `store_id`: Store identifier
- `stock`: Current stock quantity
- `mrp`: Maximum retail price
- `discount`: Current discount
- `aisle`, `rack`, `shelf`: Location info
- `created_at`, `updated_at`: Timestamps

### Order
- `id`: Primary key
- `order_id`: External order ID
- `reference_number`: Unique order reference
- `customer_id`: Customer identifier
- `status`: PENDING, PACKED, SHIPPED
- `picking_status`: NOT_STARTED, IN_PROGRESS, COMPLETED
- `amount`, `discount`, `shipping`: Order details
- `items`: List of OrderItem
- `crate_labels`: List of CrateLabel
- `created_at`, `updated_at`: Timestamps

### OrderItem
- `id`: Primary key
- `order_id`: FK to Order
- `product_id`: FK to Product
- `ordered_quantity`: Quantity ordered
- `picked_quantity`: Quantity picked
- `status`: PENDING, PICKED, PACKED
- `created_at`, `updated_at`: Timestamps

### Agent (Picker/Packer)
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Bcrypt hashed password
- `full_name`: Agent's name
- `email`: Email address
- `phone`: Phone number
- `status`: ACTIVE/INACTIVE
- `created_at`, `updated_at`: Timestamps

### PickingActivity
- `id`: Primary key
- `order_id`: FK to Order
- `product_id`: Product being picked
- `quantity`: Quantity picked
- `picking_method`: manual, qr_scan, weighing
- `picker_agent_id`: Agent who picked
- `details`: JSON details
- `picked_at`: Timestamp

### CrateLabel
- `id`: Primary key
- `order_id`: FK to Order
- `crate_label`: Label string/code
- `weight`: Crate weight
- `items_data`: JSON item list in crate
- `created_at`: Timestamp

---

## 🔄 Workflow

### 1. Order Reception
- Orders come via webhook from order service
- Order and products are created in database
- Inventory is synced

### 2. Agent Login
- Agent registers/logs in via UI or API
- Receives JWT token for subsequent requests

### 3. Order Picking
- Agent views pending orders in dashboard
- Selects order to pick
- Scans/enters products using:
  - QR Code scanner
  - Weighing machine
  - Manual entry
- Quantity is updated for each item

### 4. Order Packing
- All items picked, agent completes picking
- Creates crate labels with weights
- Confirms final package metadata

### 5. Order Completion
- Order status updated to PACKED
- Notification sent to order service
- Inventory updated to reflect picked items
- Order ready for shipping

---

## 🛠️ Service Clients

The application includes clients for external services:

### OrderServiceClient
```python
from services.order_client import OrderServiceClient

client = OrderServiceClient()
client.update_order_status(reference_number="ORD123", status="PACKED", crates=[...])
client.get_order(reference_number="ORD123")
```

### InventoryServiceClient
```python
from services.inventory_client import InventoryServiceClient

client = InventoryServiceClient()
client.update_inventory(product_id=1, store_id=1, stock=50)
client.get_inventory(product_id=1, store_id=1)
```

### CustomerServiceClient
```python
from services.customer_client import CustomerServiceClient

client = CustomerServiceClient()
client.get_customer(customer_id="CUST123")
client.update_customer(customer_id="CUST123", customer_data={...})
```

---

## 📱 Web UI Features

The application includes a comprehensive web interface at `/ui`:

### 1. **Login Page**
- Username/password authentication
- Session management with JWT tokens
- Remember me functionality
- Form validation

### 2. **Dashboard**
- Quick stats (pending orders, completed today, etc.)
- Recent activity log
- Quick actions

### 3. **Orders Page**
- List of all orders with filters (status, date range)
- Order details view
- Quick picking initiation
- Order status tracking

### 4. **Picking Interface**
- Large order details display
- Item list with checkboxes
- Product search/filter
- QR code scanner integration
- Manual quantity input
- Weighing machine integration
- Real-time progress tracking

### 5. **Packing Interface**
- Order summary
- Crate label generation
- Weight tracking
- Items per crate
- Finalize and ship

### 6. **Agent Profile**
- Edit profile information
- Change password
- Logout
- Session information

---

## 🧪 Testing

### Run Tests
```bash
pytest test_main.http
```

### Manual API Testing
Use the provided `test_main.http` file with REST Client extension in VS Code.

### API Documentation
Visit `/docs` for interactive Swagger documentation.

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///picker_app.db` | Database connection string |
| `ORDER_SERVICE_HOST` | `http://localhost:8000` | Order service URL |
| `ORGANIZATION_ID` | `5` | Organization ID |
| `ORDER_SERVICE_USER_ID` | `1` | Service user ID |
| `SECRET_KEY` | - | JWT signing key (MUST SET) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration time |
| `DEBUG` | `False` | Debug mode |

---

## 📦 Dependencies

See `requirements.txt` for all dependencies. Main packages:

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **httpx** - HTTP client
- **uvicorn** - ASGI server

---

## 🐛 Troubleshooting

### Database Connection Error
```
Check DATABASE_URL in .env
Ensure database file/server is accessible
```

### Authentication Failed
```
Verify SECRET_KEY is set in .env
Check agent username/password
Verify JWT_ALGORITHM matches token creation
```

### Service Integration Issues
```
Check ORDER_SERVICE_HOST is correct
Verify network connectivity
Review service client logs
```

### Port Already in Use
```bash
# Change port in main.py or run:
uvicorn main:app --port 8001
```

---

## 📝 Development Notes

### Adding New Endpoints
1. Create controller in `controllers/`
2. Define schemas in `controllers/schemas.py`
3. Implement logic in `services/` if complex
4. Include router in `main.py`

### Adding New Models
1. Create model file in `models/`
2. Include CRUD functions in same file
3. Export in `models/__init__.py`
4. Update schema in `controllers/schemas.py`

### Database Migrations
- SQLAlchemy automatically creates tables on startup
- For production, consider using Alembic for migrations

---

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Production Setup
```bash
# Use production database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@host/db

# Use proper secret key
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check application logs
4. Review test cases in `test_main.http`

---

## 📄 License

Internal use only.

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Status**: Production Ready
