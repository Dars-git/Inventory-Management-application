# Inventory Management Application

## Description

This project is a web application built using Flask, a micro web framework for Python. It serves as a platform for managing orders, products, and users within a business environment.

## Features

- **User Authentication**: Allows users to register, login, and logout securely.
- **Dashboard**: Provides a dashboard with statistics such as daily orders count and total number of orders.
- **Order Management**: Allows users to create, update, and delete orders. Handles order items and calculates total amounts.
- **Product Management**: Enables users to manage products, including adding, updating, and deleting products.
- **Role-based Access Control**: Supports different user roles and permissions.
- **Reporting**: Generates reports of all orders and their details.
- **Printable Invoices**: Provides printable invoices for individual orders.

## Installation

1. Clone the repository:

```
git clone <repository_url>
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Set up the database:

```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

4. Run the application:

```
python run.py
```

## Usage

- Access the application in your web browser by navigating to `http://localhost:5000`.
- Register or login to access the dashboard and manage orders, products, and users.
- Explore different functionalities such as creating orders, managing products, and generating reports.

