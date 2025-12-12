<div align="center">
<h1>🛍️ Billing & Inventory Management System (Swapnil)</h1>
<p>
<b>A full-stack, offline desktop application tailored for high-speed seasonal retail.</b>
</p>

<p>
<a href="https://www.python.org/">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.10%252B-blue%3Fstyle%3Dflat%26logo%3Dpython%26logoColor%3Dwhite" alt="Python">
</a>
<a href="https://www.mysql.com/">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/MySQL-8.0%252B-00758F%3Fstyle%3Dflat%26logo%3Dmysql%26logoColor%3Dwhite" alt="MySQL">
</a>
<img src="https://www.google.com/search?q=https://img.shields.io/badge/GUI-Tkinter-green%3Fstyle%3Dflat" alt="Tkinter">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Status-Active-success%3Fstyle%3Dflat" alt="Status">
</p>

</div>

<br />

📋 Table of Contents

Overview

Key Features

Technology Stack

Getting Started

Prerequisites

Installation

Configuration

Usage Guide

Project Structure

License

<br />

📖 Overview

This system is specifically designed for seasonal shops (e.g., festival
 goods, clothing, firecrackers) located in regions like Sangli, Maharashtra,
 where offline reliability and speed are critical. It replaces manual
  bookkeeping with a digitized, automated workflow.

  Primary Goal: Enable high-speed billing during peak seasons while tracking
   inventory in real-time.

   <br />

🚀 Key Features
🛒 Point of Sale (POS)

Instant Search: Find products by name or ID instantly.

Auto-Calculation: Real-time computation of Subtotal, GST, and Grand Total.

PDF Invoicing: Generates professional, grid-based PDF receipts using
 ReportLab.

Cart Controls: Dynamic quantity adjustments and item removal.

📦 Inventory Control

Real-time Tracking: Stock levels update automatically after every sale.

Visual Alerts: Rows turn <span style="color:red">red</span> when stock dips
 below the minimum threshold.

Bulk Import: Import thousands of items via .csv to set up the shop in minutes.

📊 Analytics & Insights

Sales Dashboard: View total revenue and transaction counts.

Visual Graphs: Daily sales performance visualized with Matplotlib.

Export Data: Download detailed reports to Excel/CSV for further analysis.

🔐 Security

Role-Based Access: - Admin: Full access to inventory, users, and reports.

Staff: Restricted to billing functions only.

Encryption: Passwords are hashed using SHA-256.

<br />

🛠️ Technology Stack

Language : Python 3.x

Interface : Tkinter

Database : MySQL

Reports : ReportLab PDF Invoice Generation

Analytics : Pandas / Matplotlib

<br />

⚡ Getting Started

Prerequisites

Python 3.10+

MySQL Server (Running locally or remotely)

Installation

1. Clone the Repository
    git clone [https://github.com/yourusername/billing-system.git](https://
    github.com/yourusername/billing-system.git)
    cd billing-system
    
2. Install Dependancies 
    pip install pandas matplotlib reportlab mysql-connector-python
Configuration
    1. Open database.py.
    2. Update the MySQL connection settings to match your local server:
        self.host = "localhost"
        self.user = "root"       # Update if different
        self.password = "852456" # Update if different

3. Run the app 
    python main.py

Note: The database shop_inventory and all tables are created automatically on
 the first run.

<br/>

🔑 Usage Guide

Default Login 
Upon first launch use the folloeing credentials to access te system : 
    username : admin 
    password : admin123

Common Workflows

1. Adding Stock: Login as Admin → Go to Inventory → Click Import CSV or Add 
New Item.

2. Billing: Login as Staff/Admin → Go to Billing → Search Item → Add to Cart
→ Click Generate Bill.

3. Viewing Reports: Go to Analytics → Click Show Sales Summary.

<br />

📂 Project Structure
billing-system/
├── invoices/           # 📄 Generated PDF receipts stored here
├── main.py             # 🖥️ Main GUI application & Event logic
├── database.py         # 🗄️ Database connection & Query logic
├── requirements.txt    # 📦 List of python dependencies
└── README.md           # 📘 Project documentation

<br/>

📝 License

This project is open-source and available under the MIT License.

<div align="center">
<sub>Designed & Developed by Swapnil</sub>
</div>
