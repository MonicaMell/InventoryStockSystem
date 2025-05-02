import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from inventory import (
    get_total_stock, get_total_value, check_low_stock, get_receipt_history,
    get_purchase_history, add_new_item, get_all_categories, search_items,
    create_purchase_order, receive_purchase_order, get_pending_orders
)
from db import connect_db

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Purchasing System")
        self.root.geometry("1200x800")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Accent.TButton', foreground='white', background='#0078d7')
        self.style.configure('Warning.TLabel', foreground='red')
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_new_item_tab()
        self.create_manage_stock_tab()
        self.create_purchasing_tab()
        self.create_reports_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status()
    
    def update_status(self):
        total_stock = get_total_stock()
        total_value = get_total_value()
        self.status_var.set(f"Total Stock: {total_stock} | Total Inventory Value: ${total_value:.2f}")
        self.root.after(5000, self.update_status)
    
    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Refresh button
        refresh_frame = ttk.Frame(self.dashboard_tab)
        refresh_frame.pack(pady=5, padx=10, fill='x')
        ttk.Button(refresh_frame, text="Refresh Dashboard", command=self.refresh_dashboard).pack(side='right')
        
        # Summary frame
        self.summary_frame = ttk.LabelFrame(self.dashboard_tab, text="Inventory Summary")
        self.summary_frame.pack(pady=10, padx=10, fill='x')
        
        # Low stock warning
        self.low_stock_frame = ttk.LabelFrame(self.dashboard_tab, text="Low Stock Alerts")
        self.low_stock_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Recent receipts
        self.receipts_frame = ttk.LabelFrame(self.dashboard_tab, text="Recent Receipts")
        self.receipts_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Recent purchases
        self.purchases_frame = ttk.LabelFrame(self.dashboard_tab, text="Recent Purchases")
        self.purchases_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Initial load
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        # Clear existing widgets
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        for widget in self.low_stock_frame.winfo_children():
            widget.destroy()
        for widget in self.receipts_frame.winfo_children():
            widget.destroy()
        for widget in self.purchases_frame.winfo_children():
            widget.destroy()
        
        # Summary
        total_stock = get_total_stock()
        total_value = get_total_value()
        
        ttk.Label(self.summary_frame, text=f"Total Items in Stock: {total_stock}").pack(anchor='w')
        ttk.Label(self.summary_frame, text=f"Total Inventory Value: ${total_value:.2f}").pack(anchor='w')
        
        # Low stock items
        low_stock_items = check_low_stock()
        if low_stock_items:
            for item in low_stock_items:
                frame = ttk.Frame(self.low_stock_frame)
                frame.pack(fill='x', pady=2)
                ttk.Label(frame, text=f"{item[0]} - Only {item[1]} left (min: {item[2]})", 
                         style='Warning.TLabel' if item[1] <= 2 else '').pack(side='left')
        else:
            ttk.Label(self.low_stock_frame, text="No low stock items").pack()
        
        # Recent receipts
        receipts = get_receipt_history()[:5]
        if receipts:
            for receipt in receipts:
                frame = ttk.Frame(self.receipts_frame)
                frame.pack(fill='x', pady=2)
                ttk.Label(frame, text=f"{receipt[0]} - {receipt[1]} units on {receipt[2][:10]} from {receipt[3]}").pack(anchor='w')
        else:
            ttk.Label(self.receipts_frame, text="No receipt history").pack()
        
        # Recent purchases
        purchases = get_purchase_history()[:5]
        if purchases:
            for purchase in purchases:
                frame = ttk.Frame(self.purchases_frame)
                frame.pack(fill='x', pady=2)
                
                # Parse ISO format datetime
                purchase_datetime = datetime.fromisoformat(purchase[2].replace('Z', ''))
                formatted_date = purchase_datetime.strftime("%H:%M %d-%m-%y")
                
                status_color = 'red' if purchase[4] == 'Pending' else 'green'
                ttk.Label(frame, 
                        text=f"{purchase[0]} - {purchase[1]} units ordered by {purchase[3]} on {formatted_date}"
                        ).pack(anchor='w')
                ttk.Label(frame, 
                        text=f"Status: {purchase[4]}", 
                        foreground=status_color
                        ).pack(anchor='w')
        else:
            ttk.Label(self.purchases_frame, text="No purchase history").pack()
    
    def create_new_item_tab(self):
        self.new_item_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.new_item_tab, text="New Item")
        
        # Form frame
        form_frame = ttk.LabelFrame(self.new_item_tab, text="Item Information")
        form_frame.pack(pady=10, padx=10, fill='x')
        
        # Form fields
        fields = [
            ("Item Name:", "name_entry"),
            ("Price:", "price_entry"),
            ("Initial Quantity:", "quantity_entry"),
            ("Supplier:", "supplier_entry"),
            ("Category:", "category_entry"),
            ("Min Stock Level:", "min_stock_entry")
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='we')
            setattr(self, var_name, entry)
        
        # Set default min stock level
        self.min_stock_entry.insert(0, "5")
        
        # Add Item button
        button_frame = ttk.Frame(self.new_item_tab)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add to Inventory", command=self.add_new_item, 
                 style='Accent.TButton').pack(pady=10, ipadx=20, ipady=5)
    
    def add_new_item(self):
        try:
            name = self.name_entry.get()
            price = float(self.price_entry.get())
            quantity = int(self.quantity_entry.get())
            supplier = self.supplier_entry.get() or None
            category = self.category_entry.get() or None
            min_stock = int(self.min_stock_entry.get())
            
            if not name:
                raise ValueError("Item name is required")
            if price <= 0:
                raise ValueError("Price must be positive")
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            if min_stock < 0:
                raise ValueError("Minimum stock level cannot be negative")
            
            add_new_item(name, price, quantity, supplier, category)
            
            # Update min stock level
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE items SET min_stock_level = ? WHERE name = ?', (min_stock, name))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Item added to inventory successfully!")
            
            # Clear the form
            for entry in [self.name_entry, self.price_entry, self.quantity_entry, 
                        self.supplier_entry, self.category_entry, self.min_stock_entry]:
                entry.delete(0, tk.END)
            self.min_stock_entry.insert(0, "5")
            
            self.refresh_dashboard()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    def create_manage_stock_tab(self):
        self.manage_stock_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_stock_tab, text="Manage Stock")

         # Add Refresh Button at the top
        refresh_frame = ttk.Frame(self.manage_stock_tab)
        refresh_frame.pack(pady=5, padx=10, fill='x')
        ttk.Button(refresh_frame, text="Refresh", command=self.refresh_stock_list).pack(side='right')
        
        # Search Criteria Frame
        search_frame = ttk.LabelFrame(self.manage_stock_tab, text="Search Items")
        search_frame.pack(pady=10, padx=10, fill='x')
        
        # Name
        ttk.Label(search_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.search_name_entry = ttk.Entry(search_frame)
        self.search_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        # Category
        ttk.Label(search_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.search_category_combo = ttk.Combobox(search_frame, state="readonly")
        self.search_category_combo.grid(row=0, column=3, padx=5, pady=5, sticky='we')
        
        # Supplier
        ttk.Label(search_frame, text="Supplier:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.search_supplier_entry = ttk.Entry(search_frame)
        self.search_supplier_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        # Stock Level
        ttk.Label(search_frame, text="Stock Level:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.search_stock_combo = ttk.Combobox(search_frame, 
                                             values=["Any", "Low", "Medium", "High"],
                                             state="readonly")
        self.search_stock_combo.current(0)
        self.search_stock_combo.grid(row=1, column=3, padx=5, pady=5, sticky='we')
        
        # Search Button
        ttk.Button(search_frame, text="Search", command=self.search_items).grid(
            row=2, column=0, columnspan=4, pady=5, sticky='we')
        
        # Results Treeview
        tree_frame = ttk.Frame(self.manage_stock_tab)
        tree_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.items_tree = ttk.Treeview(tree_frame, 
                                     columns=('name', 'price', 'quantity', 'supplier', 'category', 'min_stock'),
                                     show='headings')
        
        # Configure columns
        self.items_tree.heading('name', text='Name')
        self.items_tree.heading('price', text='Price')
        self.items_tree.heading('quantity', text='In Stock')
        self.items_tree.heading('supplier', text='Supplier')
        self.items_tree.heading('category', text='Category')
        self.items_tree.heading('min_stock', text='Min Stock')
        
        self.items_tree.column('name', width=200)
        self.items_tree.column('price', width=80, anchor='e')
        self.items_tree.column('quantity', width=80, anchor='e')
        self.items_tree.column('supplier', width=150)
        self.items_tree.column('category', width=150)
        self.items_tree.column('min_stock', width=80, anchor='e')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.items_tree.pack(fill='both', expand=True)
        
        # Stock Management Frame
        manage_frame = ttk.LabelFrame(self.manage_stock_tab, text="Stock Management")
        manage_frame.pack(pady=10, padx=10, fill='x')
        
        # Quantity adjustment
        ttk.Label(manage_frame, text="Adjust Quantity:").grid(row=0, column=0, padx=5, pady=5)
        self.adjust_action = tk.StringVar(value="+")
        ttk.OptionMenu(manage_frame, self.adjust_action, "+", "+", "-", "=").grid(row=0, column=1, padx=5)
        self.adjust_qty_entry = ttk.Entry(manage_frame, width=10)
        self.adjust_qty_entry.grid(row=0, column=2, padx=5)
        ttk.Button(manage_frame, text="Apply", command=self.adjust_stock).grid(row=0, column=3, padx=5)
        
        # Price update
        ttk.Label(manage_frame, text="New Price:").grid(row=1, column=0, padx=5, pady=5)
        self.new_price_entry = ttk.Entry(manage_frame, width=10)
        self.new_price_entry.grid(row=1, column=1, padx=5)
        ttk.Button(manage_frame, text="Update Price", command=self.update_price).grid(row=1, column=2, columnspan=2, padx=5)
        
        # Min stock level update
        ttk.Label(manage_frame, text="Min Stock Level:").grid(row=2, column=0, padx=5, pady=5)
        self.new_min_stock_entry = ttk.Entry(manage_frame, width=10)
        self.new_min_stock_entry.grid(row=2, column=1, padx=5)
        ttk.Button(manage_frame, text="Update Min Stock", command=self.update_min_stock).grid(row=2, column=2, columnspan=2, padx=5)
        
        # Load initial data
        self.load_categories()
        self.search_items()

    def refresh_stock_list(self):
        """Refresh the items list in the Manage Stock tab"""
        # Clear search fields
        self.search_name_entry.delete(0, tk.END)
        self.search_supplier_entry.delete(0, tk.END)
        self.search_category_combo.set("All Categories")
        self.search_stock_combo.set("Any")

        # Reload categories (in case new ones were added)
        self.load_categories()

        # Refresh the items list
        self.search_items()

        # Show confirmation
        self.status_var.set("Stock list refreshed at " + datetime.now().strftime("%H:%M"))
    
    def load_categories(self):
        categories = get_all_categories()
        self.search_category_combo['values'] = ["All Categories"] + categories
        self.search_category_combo.current(0)
    
    def search_items(self):
        name = self.search_name_entry.get().strip()
        category = self.search_category_combo.get()
        supplier = self.search_supplier_entry.get().strip()
        stock_level = self.search_stock_combo.get()
        
        if category == "All Categories":
            category = None
        if not supplier:
            supplier = None
        
        results = search_items(
            name=name if name else '',
            category=category,
            supplier=supplier,
            stock_level=stock_level if stock_level != "Any" else None
        )
        
        self.items_tree.delete(*self.items_tree.get_children())
        for item in results:
            self.items_tree.insert('', 'end', values=item[1:], iid=item[0])
    
    def adjust_stock(self):
        selected = self.items_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        try:
            item_id = selected
            action = self.adjust_action.get()
            change = int(self.adjust_qty_entry.get())
            
            conn = connect_db()
            cursor = conn.cursor()
            
            # Get current quantity
            cursor.execute('SELECT name, quantity FROM items WHERE id = ?', (item_id,))
            name, current_qty = cursor.fetchone()
            
            # Calculate new quantity
            if action == "+":
                new_qty = current_qty + change
            elif action == "-":
                new_qty = max(0, current_qty - change)
            else:  # "="
                new_qty = max(0, change)
            
            # Update database
            cursor.execute('UPDATE items SET quantity = ? WHERE id = ?', (new_qty, item_id))
            
            # If adding stock, record as receipt
            if action == "+":
                cursor.execute('SELECT supplier FROM items WHERE id = ?', (item_id,))
                supplier = cursor.fetchone()[0]
                cursor.execute('''
                    INSERT INTO receipts (item_id, quantity, receipt_date, supplier)
                    VALUES (?, ?, ?, ?)
                ''', (item_id, change, datetime.now().isoformat(), supplier))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Updated {name}\nNew quantity: {new_qty}")
            self.search_items()
            self.adjust_qty_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
    
    def update_price(self):
        selected = self.items_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        try:
            new_price = float(self.new_price_entry.get())
            if new_price <= 0:
                raise ValueError("Price must be positive")
            
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE items SET price = ? WHERE id = ?', (new_price, selected))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Price updated successfully!")
            self.search_items()
            self.new_price_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update price: {str(e)}")
    
    def update_min_stock(self):
        selected = self.items_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        try:
            new_min = int(self.new_min_stock_entry.get())
            if new_min < 0:
                raise ValueError("Minimum stock cannot be negative")
            
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE items SET min_stock_level = ? WHERE id = ?', (new_min, selected))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Minimum stock level updated successfully!")
            self.search_items()
            self.new_min_stock_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update minimum stock: {str(e)}")


    def load_items_for_po(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM items ORDER BY name")
        items = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.po_item_combo['values'] = items
        if items:
            self.po_item_combo.current(0)


    def load_pending_orders(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        orders = get_pending_orders()
        for order in orders:
            # Parse ISO format datetime
            purchase_datetime = datetime.fromisoformat(order[3].replace('Z', ''))
            formatted_date = purchase_datetime.strftime("%H:%M %d-%m-%y")
            
            self.orders_tree.insert('', 'end', values=(
                order[0],  # id
                order[1],  # item
                order[2],  # qty
                order[4],  # ordered_by (shown in date column)
                formatted_date  # formatted date (shown in ordered_by column)
            ))

    def create_po(self):
        item = self.po_item_combo.get()
        quantity = self.po_quantity_entry.get()
        supplier = self.po_supplier_entry.get() or None

        if not item:
            messagebox.showerror("Error", "Please select an item")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            create_purchase_order(item, quantity, supplier)
            messagebox.showinfo("Success", "Purchase order created successfully!")
            self.load_pending_orders()
            self.po_quantity_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PO: {str(e)}")

    def receive_order(self):
        selected = self.orders_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order first")
            return
        
        po_id = self.orders_tree.item(selected)['values'][0]
        try:
            item_name, qty = receive_purchase_order(po_id)
            messagebox.showinfo("Success", f"Received {qty} units of {item_name}")
            self.load_pending_orders()
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to receive order: {str(e)}")

    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        
        # Report type selection
        report_frame = ttk.LabelFrame(self.reports_tab, text="Generate Report")
        report_frame.pack(pady=10, padx=10, fill='x')
        
        self.report_type = tk.StringVar(value="stock")
        ttk.Radiobutton(report_frame, text="Current Stock", variable=self.report_type, value="stock").pack(anchor='w')
        ttk.Radiobutton(report_frame, text="Receipt History", variable=self.report_type, value="receipts").pack(anchor='w')
        ttk.Radiobutton(report_frame, text="Purchase History", variable=self.report_type, value="purchases").pack(anchor='w')
        ttk.Radiobutton(report_frame, text="Low Stock Items", variable=self.report_type, value="low_stock").pack(anchor='w')
        
        ttk.Button(report_frame, text="Generate Report", command=self.generate_report).pack(pady=10)
        
        # Report display
        self.report_text = tk.Text(self.reports_tab, wrap=tk.WORD)
        self.report_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Export button
        ttk.Button(self.reports_tab, text="Export to File", command=self.export_report).pack(pady=5)
    
    def generate_report(self):
        report_type = self.report_type.get()
        self.report_text.delete(1.0, tk.END)
        
        if report_type == "stock":
            items = search_items('')
            self.report_text.insert(tk.END, "Current Stock Report\n")
            self.report_text.insert(tk.END, "="*70 + "\n")
            self.report_text.insert(tk.END, f"{'Name':<25}{'Price':>10}{'Qty':>8}{'Min Stock':>12}{'Value':>15}\n")
            self.report_text.insert(tk.END, "-"*70 + "\n")
            
            total_value = 0
            for item in items:
                value = item[2] * item[3]
                total_value += value
                self.report_text.insert(tk.END, 
                    f"{item[1]:<25}{item[2]:>10.2f}{item[3]:>8}{item[5]:>12}{value:>15.2f}\n")
            
            self.report_text.insert(tk.END, "-"*70 + "\n")
            self.report_text.insert(tk.END, f"{'Total Value':<55}{total_value:>15.2f}\n")
        
        elif report_type == "receipts":
            receipts = get_receipt_history()
            self.report_text.insert(tk.END, "Receipt History Report\n")
            self.report_text.insert(tk.END, "="*85 + "\n")
            self.report_text.insert(tk.END, f"{'Date':<12}  {'Item':<25}  {'Qty':>6}  {'Supplier':<20}  {'Unit Price':>12}\n")
            self.report_text.insert(tk.END, "-"*85 + "\n")
            
            for receipt in receipts:
                # Get the current price of the item
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute('SELECT price FROM items WHERE name = ?', (receipt[0],))
                price = cursor.fetchone()[0]
                conn.close()
                
                self.report_text.insert(tk.END, 
                    f"{receipt[2][:10]:<12}  {receipt[0]:<25}  {receipt[1]:>6}  {receipt[3]:<20}  {price:>12.2f}\n")
        
        elif report_type == "purchases":
            purchases = get_purchase_history()
            self.report_text.insert(tk.END, "Purchase History Report\n")
            self.report_text.insert(tk.END, "="*80 + "\n")
            self.report_text.insert(tk.END, f"{'Time':<7} {'Date':<7} {'Item':<25} {'Qty':>6} {'Ordered By':<20} {'Status':>15}\n")
            self.report_text.insert(tk.END, "-"*80 + "\n")
            
            for purchase in purchases:
                # Parse ISO format datetime
                purchase_datetime = datetime.fromisoformat(purchase[2].replace('Z', ''))
                time_part = purchase_datetime.strftime("%H:%M")
                date_part = purchase_datetime.strftime("%d-%m-%y")
                status = purchase[4]
                
                self.report_text.insert(tk.END, 
                    f"{time_part:<7} {date_part:<7} {purchase[0]:<25} {purchase[1]:>6} {purchase[3]:<20}")
                self.report_text.insert(tk.END, f"  {status:>15}", f"status_{status.lower()}")
                self.report_text.insert(tk.END, "\n")
            
            self.report_text.tag_config("status_pending", foreground="red")
            self.report_text.tag_config("status_received", foreground="green")
            
        
        elif report_type == "low_stock":
            items = check_low_stock()
            self.report_text.insert(tk.END, "Low Stock Report\n")
            self.report_text.insert(tk.END, "="*70 + "\n")
            self.report_text.insert(tk.END, f"{'Item':<25}{'Qty':>8}{'Min Stock':>12}{'Price':>10}{'Value':>15}\n")
            self.report_text.insert(tk.END, "-"*70 + "\n")
            
            for item in items:
                price = item[2]
                value = price * item[1]
                self.report_text.insert(tk.END, 
                    f"{item[0]:<25}{item[1]:>8}{item[2]:>12}{price:>10.2f}{value:>15.2f}\n")
    
    def export_report(self):
        report_text = self.report_text.get(1.0, tk.END)
        if not report_text.strip():
            messagebox.showwarning("Warning", "No report to export")
            return
        
        from datetime import datetime
        filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(report_text)
            messagebox.showinfo("Success", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    

    def load_suppliers(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT supplier FROM items WHERE supplier IS NOT NULL ORDER BY supplier")
        suppliers = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.po_supplier_combo['values'] = suppliers


    def cancel_order(self):
        selected = self.orders_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order first")
            return
        
        po_id = self.orders_tree.item(selected)['values'][0]
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # 1. Get order details before deleting
            cursor.execute('''
                SELECT item_id, quantity FROM purchases WHERE id = ?
            ''', (po_id,))
            order = cursor.fetchone()
            
            if not order:
                raise ValueError("Order not found")
            
            item_id, quantity = order
            
            # 2. Restore stock
            cursor.execute('''
                UPDATE items SET quantity = quantity + ? WHERE id = ?
            ''', (quantity, item_id))
            
            # 3. Delete the order
            cursor.execute('DELETE FROM purchases WHERE id = ?', (po_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Order cancelled and stock restored")
            self.load_pending_orders()
            self.search_items_for_po()  # Refresh stock display
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {str(e)}")


    def receive_order(self):
        selected = self.orders_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order first")
            return
        
        po_id = self.orders_tree.item(selected)['values'][0]
        try:
            item_name, qty = receive_purchase_order(po_id)
            messagebox.showinfo("Success", f"Received {qty} units of {item_name}")
            self.load_pending_orders()
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to receive order: {str(e)}")


    def create_purchasing_tab(self):
        self.purchasing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.purchasing_tab, text="Purchasing")

        # Create paned window for split view
        paned = ttk.PanedWindow(self.purchasing_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left pane - Search and Create Purchase Order
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Search Frame
        search_frame = ttk.LabelFrame(left_frame, text="Search Items")
        search_frame.pack(pady=10, padx=10, fill='x')

        # Search criteria
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.po_search_entry = ttk.Entry(search_frame)
        self.po_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.po_search_entry.bind('<KeyRelease>', self.search_items_for_po)

        # Search results treeview
        self.po_search_tree = ttk.Treeview(search_frame, columns=('name', 'qty'), 
                                        show='headings', height=5)
        self.po_search_tree.heading('name', text='Item Name')
        self.po_search_tree.heading('qty', text='In Stock')
        
        self.po_search_tree.column('name', width=200)
        self.po_search_tree.column('qty', width=80, anchor='e')
        
        self.po_search_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        self.po_search_tree.bind('<<TreeviewSelect>>', self.on_po_item_select)

        # Scrollbar for search results
        scrollbar = ttk.Scrollbar(search_frame, orient="vertical", command=self.po_search_tree.yview)
        self.po_search_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky='ns')

        # Order Form Frame
        form_frame = ttk.LabelFrame(left_frame, text="Purchase Order Details")
        form_frame.pack(pady=10, padx=10, fill='x')

        # Selected item display
        ttk.Label(form_frame, text="Selected Item:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.po_selected_item = ttk.Label(form_frame, text="None", font=('TkDefaultFont', 9, 'bold'))
        self.po_selected_item.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Current stock display
        ttk.Label(form_frame, text="Current Stock:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.po_current_stock = ttk.Label(form_frame, text="0")
        self.po_current_stock.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Quantity
        ttk.Label(form_frame, text="Order Quantity:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.po_quantity_entry = ttk.Entry(form_frame)
        self.po_quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')

        # Ordered by
        ttk.Label(form_frame, text="Ordered By:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.po_ordered_by_entry = ttk.Entry(form_frame)
        self.po_ordered_by_entry.grid(row=3, column=1, padx=5, pady=5, sticky='we')

        # Create PO button
        ttk.Button(form_frame, text="Create Purchase Order", 
                command=self.create_po).grid(row=4, column=0, columnspan=2, pady=10)

        # Right pane - Pending Orders
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)

        pending_frame = ttk.LabelFrame(right_frame, text="Pending Purchase Orders")
        pending_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Treeview for pending orders
        # Treeview for pending orders
        self.orders_tree = ttk.Treeview(pending_frame, 
                                    columns=('id', 'item', 'qty', 'date', 'ordered_by'), 
                                    show='headings')
        self.orders_tree.heading('id', text='PO #')
        self.orders_tree.heading('item', text='Item')
        self.orders_tree.heading('qty', text='Qty')
        self.orders_tree.heading('date', text='Ordered By')  # This will now show who ordered
        self.orders_tree.heading('ordered_by', text='Date')  # This will now show the date

        self.orders_tree.column('id', width=50, anchor='e')
        self.orders_tree.column('item', width=150)
        self.orders_tree.column('qty', width=50, anchor='e')
        self.orders_tree.column('ordered_by', width=150)  # Ordered By
        self.orders_tree.column('date', width=100)  # Date

        # Add scrollbar
        scrollbar = ttk.Scrollbar(pending_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.orders_tree.pack(fill='both', expand=True)

        # Action buttons frame
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(pady=5, fill='x')

        # Receive button
        ttk.Button(action_frame, text="Mark as Recieved", 
                command=self.receive_order).pack(side='right', padx=5)

        # Delete button
        ttk.Button(action_frame, text="Cancel Order", 
                command=self.cancel_order).pack(side='right', padx=5)

        # Load initial data
        self.load_pending_orders()

    def search_items_for_po(self, event=None):
        search_term = self.po_search_entry.get().strip()
        if not search_term:
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, quantity
            FROM items 
            WHERE name LIKE ? 
            ORDER BY name
        ''', (f'%{search_term}%',))
        results = cursor.fetchall()
        conn.close()

        self.po_search_tree.delete(*self.po_search_tree.get_children())
        for item in results:
            self.po_search_tree.insert('', 'end', values=item[1:], iid=item[0])

    def on_po_item_select(self, event):
        selected = self.po_search_tree.focus()
        if not selected:
            return

        item_id = selected
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, quantity FROM items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        conn.close()

        if item:
            self.po_selected_item.config(text=item[0])
            self.po_current_stock.config(text=str(item[1]))
            self.po_quantity_entry.focus()

    def create_po(self):
        selected_item = self.po_selected_item.cget('text')
        if selected_item == "None":
            messagebox.showerror("Error", "Please select an item first")
            return

        quantity = self.po_quantity_entry.get()
        ordered_by = self.po_ordered_by_entry.get()

        if not ordered_by:
            messagebox.showerror("Error", "Please enter who ordered this")
            return

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            create_purchase_order(selected_item, quantity, ordered_by)
            messagebox.showinfo("Success", "Purchase order created successfully!")
            
            # Clear form
            self.po_search_entry.delete(0, tk.END)
            self.po_search_tree.delete(*self.po_search_tree.get_children())
            self.po_selected_item.config(text="None")
            self.po_current_stock.config(text="0")
            self.po_quantity_entry.delete(0, tk.END)
            
            # Refresh pending orders
            self.load_pending_orders()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PO: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()