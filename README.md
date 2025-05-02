# Inventory Purchasing System

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A desktop application for managing inventory, purchase orders, and stock levels with SQLite backend.

## Features

### Core Functionalities
- **Inventory Management**
  - Add/edit/delete items with price, quantity, and supplier details
  - Set minimum stock level alerts
  - Real-time stock quantity updates

### Purchasing System
- Create purchase orders with automatic stock reservation
- Mark orders as received/cancelled
- Automatic stock reconciliation on order changes

### Reporting
- Current stock valuation
- Purchase order history
- Low stock alerts
- Export to CSV/PDF

## Installation

1. **Prerequisites**
   - Python 3.10+
   - pip package manager

2. **Setup**
   ```bash
   git clone https://github.com/yourusername/inventory-purchasing-system.git
   cd inventory-purchasing-system
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python initialize_db.py
