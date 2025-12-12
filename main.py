import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from database import ShopDatabase

# --- Configuration ---
SHOP_NAME = "Swapnil"
SHOP_ADDRESS = "Sangli, Maharashtra, India"
CURRENCY = "₹"

class LoginWindow:
    def __init__(self, root, db, on_success):
        self.root = root
        self.db = db
        self.on_success = on_success
        self.root.title(f"Login - {SHOP_NAME}")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f0f0")
        
        frame = tk.Frame(root, bg="white", padx=20, pady=20, relief=tk.RAISED, bd=2)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="System Login", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)
        
        tk.Label(frame, text="Username:", bg="white").pack(anchor="w")
        self.user_entry = tk.Entry(frame, width=30)
        self.user_entry.pack(pady=5)
        
        tk.Label(frame, text="Password:", bg="white").pack(anchor="w")
        self.pass_entry = tk.Entry(frame, show="*", width=30)
        self.pass_entry.pack(pady=5)
        
        tk.Button(frame, text="Login", command=self.login, bg="#007bff", fg="white", width=20).pack(pady=15)
        
        self.root.bind('<Return>', lambda event: self.login())

    def login(self):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        role = self.db.verify_login(user, pwd)
        
        if role:
            self.root.withdraw()  # Hide login window
            self.on_success(role, user)
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

class MainApplication:
    def __init__(self, root, db, role, username):
        self.root = root
        self.db = db
        self.role = role
        self.username = username
        self.cart = [] # List of tuples (id, name, price, qty, total)
        self.current_financials = {'subtotal': 0.0, 'discount': 0.0, 'tax': 0.0, 'grand_total': 0.0}
        
        self.root.title(f"{SHOP_NAME} - Management System | Logged in as: {username} ({role})")
        self.root.geometry("1280x720")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Main Layout
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        self.create_billing_tab()
        self.create_inventory_tab()
        self.create_reports_tab()
        
        if role == 'Admin':
            self.create_admin_tab()

    def create_billing_tab(self):
        self.bill_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bill_frame, text="  Billing (POS)  ")
        
        # Split Layout: Left (Product Search/Grid), Right (Cart/Totals)
        left_panel = tk.Frame(self.bill_frame, padx=10, pady=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_panel = tk.Frame(self.bill_frame, padx=10, pady=10, bg="#f8f9fa", width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # --- Left Panel: Search & Product Info ---
        search_frame = tk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=5)
        tk.Label(search_frame, text="Search Product:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_product_list)
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Product List Treeview
        cols = ("ID", "Name", "Category", "Price", "Stock")
        self.prod_tree = ttk.Treeview(left_panel, columns=cols, show="headings", height=15)
        for col in cols:
            self.prod_tree.heading(col, text=col, anchor="center") # Centered Header
            self.prod_tree.column(col, width=80, anchor="center")  # Centered Data
        self.prod_tree.column("Name", width=200, anchor="center")
        self.prod_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add to Cart Controls
        control_frame = tk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(control_frame, text="Quantity:").pack(side=tk.LEFT)
        self.qty_entry = tk.Entry(control_frame, width=10)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Add to Cart", command=self.add_to_cart, bg="#28a745", fg="white").pack(side=tk.LEFT, padx=10)
        
        # --- Right Panel: Cart & Checkout ---
        tk.Label(right_panel, text="Current Bill", font=("Arial", 14, "bold"), bg="#f8f9fa").pack(pady=5)
        
        cart_cols = ("Name", "Qty", "Total")
        self.cart_tree = ttk.Treeview(right_panel, columns=cart_cols, show="headings", height=15)
        self.cart_tree.heading("Name", text="Item", anchor="center")
        self.cart_tree.heading("Qty", text="Qty", anchor="center")
        self.cart_tree.heading("Total", text="Total", anchor="center")
        self.cart_tree.column("Name", width=120, anchor="center")
        self.cart_tree.column("Qty", width=40, anchor="center")
        self.cart_tree.column("Total", width=60, anchor="center")
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Financials
        self.total_lbl = tk.Label(right_panel, text=f"Subtotal: {CURRENCY} 0.00", font=("Arial", 12), bg="#f8f9fa", anchor="e")
        self.total_lbl.pack(fill=tk.X, pady=2)
        
        tk.Label(right_panel, text="Discount (%):", bg="#f8f9fa").pack(anchor="w")
        self.disc_entry = tk.Entry(right_panel)
        self.disc_entry.insert(0, "0")
        self.disc_entry.pack(fill=tk.X)
        
        tk.Label(right_panel, text="Tax (%):", bg="#f8f9fa").pack(anchor="w")
        self.tax_entry = tk.Entry(right_panel)
        self.tax_entry.insert(0, "0") 
        self.tax_entry.pack(fill=tk.X)
        
        tk.Button(right_panel, text="Calculate Total", command=self.update_totals).pack(fill=tk.X, pady=5)
        
        self.final_lbl = tk.Label(right_panel, text=f"Grand Total: {CURRENCY} 0.00", font=("Arial", 16, "bold"), fg="red", bg="#f8f9fa")
        self.final_lbl.pack(pady=10)
        
        tk.Button(right_panel, text="GENERATE BILL & PRINT", command=self.checkout, bg="#007bff", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill=tk.X, pady=10)
        tk.Button(right_panel, text="Clear Cart", command=self.clear_cart, bg="gray", fg="white").pack(fill=tk.X)

        self.update_product_list()

    def create_inventory_tab(self):
        self.inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inv_frame, text="  Inventory  ")
        
        # Tools Frame
        tools_frame = tk.Frame(self.inv_frame, pady=10)
        tools_frame.pack(fill=tk.X)
        
        tk.Button(tools_frame, text="Add New Item", command=self.popup_add_item).pack(side=tk.LEFT, padx=10)
        tk.Button(tools_frame, text="Refresh", command=self.load_inventory_table).pack(side=tk.LEFT, padx=10)
        tk.Button(tools_frame, text="Import CSV", command=self.import_csv).pack(side=tk.RIGHT, padx=10)
        
        # Inventory Table
        cols = ("ID", "Name", "Category", "Price", "Stock", "Min Stock")
        self.inv_tree = ttk.Treeview(self.inv_frame, columns=cols, show="headings")
        for col in cols:
            self.inv_tree.heading(col, text=col, anchor="center") # Centered Header
            self.inv_tree.column(col, anchor="center")            # Centered Data
        
        # Configure tags for low stock
        self.inv_tree.tag_configure('low_stock', background='#ffcccc') # Light red
        
        self.inv_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Edit/Delete Buttons
        action_frame = tk.Frame(self.inv_frame, pady=10)
        action_frame.pack(fill=tk.X)
        tk.Button(action_frame, text="Delete Selected", command=self.delete_item, bg="#dc3545", fg="white").pack(side=tk.RIGHT, padx=10)
        tk.Button(action_frame, text="Update Selected", command=self.popup_update_item).pack(side=tk.RIGHT, padx=10)

        self.load_inventory_table()

    def create_reports_tab(self):
        self.rep_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rep_frame, text="  Analytics & Reports  ")
        
        # Controls
        ctrl_frame = tk.Frame(self.rep_frame, pady=10, padx=10)
        ctrl_frame.pack(fill=tk.X)
        
        tk.Button(ctrl_frame, text="Show Sales Summary", command=self.show_sales_summary).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Show Top Selling Items", command=self.show_top_items).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Low Stock Report", command=self.show_low_stock).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Export to Excel", command=self.export_report).pack(side=tk.RIGHT, padx=5)
        
        # Content Area (Text/Table + Graph)
        self.rep_content = tk.Frame(self.rep_frame)
        self.rep_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.rep_text = tk.Text(self.rep_content, height=10)
        self.rep_text.pack(fill=tk.X)
        
        # Placeholder for Matplotlib graph
        self.graph_frame = tk.Frame(self.rep_content, bg="white")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def create_admin_tab(self):
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="  Admin  ")
        
        tk.Label(admin_frame, text="User Management", font=("Arial", 14, "bold")).pack(pady=20)
        
        form_frame = tk.Frame(admin_frame)
        form_frame.pack()
        
        tk.Label(form_frame, text="New Username:").grid(row=0, column=0, padx=5, pady=5)
        new_user = tk.Entry(form_frame)
        new_user.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="New Password:").grid(row=1, column=0, padx=5, pady=5)
        new_pass = tk.Entry(form_frame, show="*")
        new_pass.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Role:").grid(row=2, column=0, padx=5, pady=5)
        role_combo = ttk.Combobox(form_frame, values=["Staff", "Admin"])
        role_combo.current(0)
        role_combo.grid(row=2, column=1, padx=5, pady=5)
        
        def add_user_handler():
            if self.db.add_user(new_user.get(), new_pass.get(), role_combo.get()):
                messagebox.showinfo("Success", "User added successfully!")
                new_user.delete(0, tk.END)
                new_pass.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Username already exists!")
                
        tk.Button(form_frame, text="Create User", command=add_user_handler, bg="#28a745", fg="white").grid(row=3, columnspan=2, pady=10)

    # --- Billing Logic ---
    def update_product_list(self, *args):
        query = self.search_var.get()
        # Clear current list
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        
        if query:
            products = self.db.search_products(query)
        else:
            products = self.db.get_all_products()
            
        for p in products:
            self.prod_tree.insert("", "end", values=p)

    def add_to_cart(self):
        selected = self.prod_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product first.")
            return
            
        item_vals = self.prod_tree.item(selected[0])['values']
        
        # Robust unpacking
        try:
            pid = item_vals[0]
            name = item_vals[1]
            price = float(item_vals[3]) 
            stock = int(item_vals[4])   
        except IndexError:
            messagebox.showerror("Error", "Could not retrieve item data.")
            return
        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock data.")
            return

        try:
            qty = int(self.qty_entry.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid Quantity")
            return
            
        if qty > stock:
            messagebox.showerror("Error", f"Insufficient Stock! Only {stock} available.")
            return
            
        total = price * qty
        self.cart.append((pid, name, price, qty, total))
        self.update_cart_display()
        self.update_totals()

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        for item in self.cart:
            # item: (pid, name, price, qty, total)
            self.cart_tree.insert("", "end", values=(item[1], item[3], f"{item[4]:.2f}"))

    def update_totals(self):
        subtotal = sum(item[4] for item in self.cart)
        self.total_lbl.config(text=f"Subtotal: {CURRENCY} {subtotal:.2f}")
        
        try:
            disc_per = float(self.disc_entry.get())
            tax_per = float(self.tax_entry.get())
        except ValueError:
            disc_per = 0
            tax_per = 0
            
        discount = (subtotal * disc_per) / 100
        tax = ((subtotal - discount) * tax_per) / 100
        grand_total = subtotal - discount + tax
        
        self.current_financials = {
            'subtotal': subtotal,
            'discount': discount,
            'tax': tax,
            'grand_total': grand_total
        }
        
        self.final_lbl.config(text=f"Grand Total: {CURRENCY} {grand_total:.2f}")

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()
        self.update_totals()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Cannot generate bill for empty cart.")
            return
            
        self.update_totals()
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if self.db.process_sale(invoice_id, None, self.cart, self.current_financials):
            self.generate_pdf(invoice_id)
            messagebox.showinfo("Success", "Transaction Completed & Invoice Saved!")
            self.clear_cart()
            self.load_inventory_table() # Refresh inventory
            self.update_product_list()
        else:
            messagebox.showerror("Error", "Transaction Failed.")

    def generate_pdf(self, invoice_id):
        if not os.path.exists("invoices"):
            os.makedirs("invoices")
            
        filename = f"invoices/{invoice_id}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 750, SHOP_NAME)
        c.setFont("Helvetica", 10)
        c.drawString(50, 735, SHOP_ADDRESS)
        c.drawString(50, 720, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, 705, f"Invoice #: {invoice_id}")
        
        c.line(50, 690, 550, 690)
        
        # --- PDF Table Generation ---
        # Data Preparation
        data = [['Item', 'Price', 'Qty', 'Total']]
        for item in self.cart:
            # item: (pid, name, price, qty, total)
            data.append([item[1], f"{item[2]:.2f}", str(item[3]), f"{item[4]:.2f}"])
            
        # Add Totals as rows in the table for alignment
        # Only showing GST and Total Amount as requested
        data.append(['', '', 'GST', f"+{self.current_financials['tax']:.2f}"])
        data.append(['', '', 'Total Amount', f"{self.current_financials['grand_total']:.2f}"])

        # Table Layout - Increased column widths for better spacing (Total width: 480)
        table = Table(data, colWidths=[200, 80, 100, 100])
        
        # Table Style
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),      # Header Background
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),           # Header Text Color
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),                  # Center Align Everything
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),        # Header Font
            ('BOTTOMPADDING', (0,0), (-1,0), 12),                 # Header Padding
            ('GRID', (0,0), (-1,-1), 1, colors.black),            # Grid Borders for All Cells
            ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),     # Bold Grand Total
            ('BACKGROUND', (-1,-1), (-1,-1), colors.whitesmoke),  # Highlight Grand Total
        ])
        table.setStyle(style)
        
        # Draw Table on Canvas
        w, h = table.wrapOn(c, 500, 500)
        # Position: 50 from left, and top is at 650. 
        # y = 650 - h ensures the table hangs down from y=650
        table.drawOn(c, 50, 650-h)
        
        # Footer (Dynamic position based on table height)
        footer_y = 650 - h - 50
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(300, footer_y, f"Thank you for shopping at {SHOP_NAME}! Please Visit Again.")
        
        c.save()
        # On Windows, try to open the file
        try:
            os.startfile(os.path.abspath(filename))
        except:
            pass

    # --- Inventory Logic ---
    def load_inventory_table(self):
        for i in self.inv_tree.get_children():
            self.inv_tree.delete(i)
        
        products = self.db.get_all_products()
        for p in products:
            # Check for low stock
            tags = ()
            stock = p[4]
            min_stock = p[5]
            if stock <= min_stock:
                tags = ('low_stock',)
            self.inv_tree.insert("", "end", values=p, tags=tags)

    def popup_add_item(self):
        # Simple popup logic using simpledialog or a Toplevel
        top = tk.Toplevel(self.root)
        top.title("Add Product")
        
        tk.Label(top, text="Name:").grid(row=0, column=0)
        e_name = tk.Entry(top); e_name.grid(row=0, column=1)
        
        tk.Label(top, text="Category:").grid(row=1, column=0)
        e_cat = tk.Entry(top); e_cat.grid(row=1, column=1)
        
        tk.Label(top, text="Price:").grid(row=2, column=0)
        e_price = tk.Entry(top); e_price.grid(row=2, column=1)
        
        tk.Label(top, text="Stock:").grid(row=3, column=0)
        e_stock = tk.Entry(top); e_stock.grid(row=3, column=1)

        tk.Label(top, text="Min Stock Alert:").grid(row=4, column=0)
        e_min = tk.Entry(top); e_min.insert(0, "10"); e_min.grid(row=4, column=1)
        
        def save():
            try:
                self.db.add_product(e_name.get(), e_cat.get(), float(e_price.get()), int(e_stock.get()), int(e_min.get()))
                self.load_inventory_table()
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric values")
                
        tk.Button(top, text="Save", command=save).grid(row=5, columnspan=2, pady=10)

    def popup_update_item(self):
        selected = self.inv_tree.selection()
        if not selected: return
        item_vals = self.inv_tree.item(selected[0])['values']
        
        top = tk.Toplevel(self.root)
        top.title("Update Product")
        
        tk.Label(top, text="Name:").grid(row=0, column=0)
        e_name = tk.Entry(top); e_name.insert(0, item_vals[1]); e_name.grid(row=0, column=1)
        
        tk.Label(top, text="Category:").grid(row=1, column=0)
        e_cat = tk.Entry(top); e_cat.insert(0, item_vals[2]); e_cat.grid(row=1, column=1)
        
        tk.Label(top, text="Price:").grid(row=2, column=0)
        e_price = tk.Entry(top); e_price.insert(0, item_vals[3]); e_price.grid(row=2, column=1)
        
        tk.Label(top, text="Stock:").grid(row=3, column=0)
        e_stock = tk.Entry(top); e_stock.insert(0, item_vals[4]); e_stock.grid(row=3, column=1)

        tk.Label(top, text="Min Stock:").grid(row=4, column=0)
        e_min = tk.Entry(top); e_min.insert(0, item_vals[5]); e_min.grid(row=4, column=1)
        
        def save():
            self.db.update_product(item_vals[0], e_name.get(), e_cat.get(), float(e_price.get()), int(e_stock.get()), int(e_min.get()))
            self.load_inventory_table()
            top.destroy()
            
        tk.Button(top, text="Update", command=save).grid(row=5, columnspan=2)

    def delete_item(self):
        selected = self.inv_tree.selection()
        if not selected: return
        if messagebox.askyesno("Confirm", "Delete selected item?"):
            pid = self.inv_tree.item(selected[0])['values'][0]
            self.db.delete_product(pid)
            self.load_inventory_table()

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                # Expected columns: name, category, price, stock, min_stock
                count = 0
                for index, row in df.iterrows():
                    self.db.add_product(row['name'], row['category'], row['price'], row['stock'], row['min_stock'])
                    count += 1
                messagebox.showinfo("Success", f"Imported {count} items successfully.")
                self.load_inventory_table()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {e}")

    # --- Reports Logic ---
    def show_sales_summary(self):
        df = self.db.get_sales_data()
        if df.empty:
            self.rep_text.delete(1.0, tk.END)
            self.rep_text.insert(tk.END, "No sales data found.")
            return

        total_rev = df['grand_total'].sum()
        count = len(df)
        self.rep_text.delete(1.0, tk.END)
        self.rep_text.insert(tk.END, f"Total Invoices: {count}\n")
        self.rep_text.insert(tk.END, f"Total Revenue: {CURRENCY} {total_rev:.2f}\n")
        
        # Plot
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        # Group by Date (Daily Sales)
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby(df['date'].dt.date)['grand_total'].sum()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        daily.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title("Daily Sales Revenue")
        ax.set_ylabel("Revenue")
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_top_items(self):
        df = self.db.get_item_sales_data()
        if df.empty:
            return
            
        top_items = df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
        
        self.rep_text.delete(1.0, tk.END)
        self.rep_text.insert(tk.END, "Top Selling Items:\n")
        self.rep_text.insert(tk.END, top_items.to_string())
        
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(6, 4))
        top_items.plot(kind='barh', ax=ax, color='lightgreen')
        ax.set_title("Top Selling Items (Qty)")
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_low_stock(self):
        df = self.db.get_inventory_data()
        low_stock = df[df['stock'] <= df['min_stock']]
        
        self.rep_text.delete(1.0, tk.END)
        self.rep_text.insert(tk.END, "CRITICAL: Low Stock Items:\n\n")
        if low_stock.empty:
            self.rep_text.insert(tk.END, "All stock levels are healthy.")
        else:
            self.rep_text.insert(tk.END, low_stock[['name', 'stock', 'min_stock']].to_string())

    def export_report(self):
        df = self.db.get_sales_data()
        if df.empty: return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if file_path:
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", "Sales report exported successfully.")

# --- Bootstrapper ---
if __name__ == "__main__":
    db = ShopDatabase()
    
    root = tk.Tk()
    
    def on_login_success(role, username):
        app = MainApplication(root, db, role, username)
        root.deiconify() # Show main window

    # Start with Login Window
    login = LoginWindow(root, db, on_login_success)
    root.mainloop()