import os
import json
import datetime
import flet as ft
from collections import defaultdict


class BudgetManager:
    def __init__(self, filename="budget_data.json"):
        self.filename = filename
        self.data = self._load_data()
        self.categories = set(["Groceries", "Housing", "Transportation", "Entertainment", "Utilities",
                               "Healthcare", "Savings", "Debt", "Personal", "Miscellaneous"])

    def _load_data(self):
        """Load budget data from file or create new data structure"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {"income": [], "expenses": []}
        return {"income": [], "expenses": []}

    def _save_data(self):
        """Save budget data to file"""
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add_income(self, amount, source, date=None):
        """Add income to budget"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")

        self.data["income"].append({
            "amount": float(amount),
            "source": source,
            "date": date
        })
        self._save_data()
        return True

    def add_expense(self, amount, category, description, date=None):
        """Add expense to budget"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")

        if category not in self.categories:
            self.categories.add(category)

        self.data["expenses"].append({
            "amount": float(amount),
            "category": category,
            "description": description,
            "date": date
        })
        self._save_data()
        return True

    def get_summary(self, period=None):
        """Get summary of budget for specified period (default: all time)"""
        income = self._filter_by_period(self.data["income"], period)
        expenses = self._filter_by_period(self.data["expenses"], period)

        total_income = sum(item["amount"] for item in income)
        total_expenses = sum(item["amount"] for item in expenses)
        balance = total_income - total_expenses

        # Calculate expenses by category
        expenses_by_category = defaultdict(float)
        for expense in expenses:
            expenses_by_category[expense["category"]] += expense["amount"]

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,
            "expenses_by_category": dict(expenses_by_category)
        }

    def _filter_by_period(self, items, period):
        """Filter items by time period"""
        if period is None:
            return items

        today = datetime.datetime.now()

        if period == "day":
            start_date = today.strftime("%Y-%m-%d")
        elif period == "week":
            start_date = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        elif period == "month":
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        elif period == "year":
            start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        else:
            return items

        return [item for item in items if item["date"] >= start_date]

    def get_spending_advice(self):
        """Provide basic spending advice based on budget"""
        summary = self.get_summary()
        advice = []

        # If spending more than earning
        if summary["balance"] < 0:
            advice.append("⚠️ Warning: You're spending more than you earn!")

            # Find top expense categories
            categories = sorted(summary["expenses_by_category"].items(),
                                key=lambda x: x[1], reverse=True)

            if categories:
                top_category = categories[0][0]
                advice.append(f"Consider cutting back on {top_category}, your highest expense category.")

        # If savings percentage is low
        savings = summary["expenses_by_category"].get("Savings", 0)
        if savings < summary["total_income"] * 0.1:
            advice.append("Try to save at least 10% of your income.")

        return advice if advice else ["Your budget looks good!"]

    def get_transactions(self, transaction_type="all", limit=10):
        """Get recent transactions"""
        transactions = []

        if transaction_type == "income" or transaction_type == "all":
            for item in sorted(self.data["income"], key=lambda x: x["date"], reverse=True)[:limit]:
                transactions.append({
                    "type": "Income",
                    "date": item['date'],
                    "amount": item['amount'],
                    "category": item['source'],
                    "description": item['source']
                })

        if transaction_type == "expenses" or transaction_type == "all":
            for item in sorted(self.data["expenses"], key=lambda x: x["date"], reverse=True)[:limit]:
                transactions.append({
                    "type": "Expense",
                    "date": item['date'],
                    "amount": item['amount'],
                    "category": item['category'],
                    "description": item['description']
                })

        return sorted(transactions, key=lambda x: x["date"], reverse=True)[:limit]


def main(page: ft.Page):
    # Initialize budget manager
    budget = BudgetManager()

    # Set page properties
    page.title = "Budget Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800
    page.padding = 20

    # Define UI components
    page.appbar = ft.AppBar(
        title=ft.Text("Budget Manager", size=30, weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
    )

    # TABS
    tab_titles = ["Dashboard", "Add Income", "Add Expense", "Transactions", "Advice"]

    # ---- DASHBOARD TAB ----
    summary_period_dropdown = ft.Dropdown(
        label="Time Period",
        options=[
            ft.dropdown.Option("all", "All Time"),
            ft.dropdown.Option("year", "This Year"),
            ft.dropdown.Option("month", "This Month"),
            ft.dropdown.Option("week", "This Week"),
            ft.dropdown.Option("day", "Today"),
        ],
        value="month",
        width=200,
    )

    income_text = ft.Text("Total Income: $0.00", size=18)
    expenses_text = ft.Text("Total Expenses: $0.00", size=18)
    balance_text = ft.Text("Balance: $0.00", size=18, weight=ft.FontWeight.BOLD)
    category_container = ft.Column(spacing=10)

    def update_dashboard():
        summary = budget.get_summary(summary_period_dropdown.value)
        income_text.value = f"Total Income: ${summary['total_income']:.2f}"
        expenses_text.value = f"Total Expenses: ${summary['total_expenses']:.2f}"

        # Update balance with color
        balance = summary['balance']
        balance_text.value = f"Balance: ${balance:.2f}"
        balance_text.color = ft.colors.GREEN if balance >= 0 else ft.colors.RED

        # Clear and update category breakdown
        category_container.controls.clear()

        # Add header
        category_container.controls.append(
            ft.Text("Expense Breakdown by Category:", size=18, weight=ft.FontWeight.BOLD)
        )

        # Sort categories by amount
        sorted_categories = sorted(
            summary['expenses_by_category'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Calculate percentages and add category rows
        for category, amount in sorted_categories:
            percentage = 0
            if summary['total_expenses'] > 0:
                percentage = (amount / summary['total_expenses'] * 100)

            category_row = ft.Row([
                ft.Text(f"{category}:", width=150),
                ft.Text(f"${amount:.2f}", width=100),
                ft.Text(f"({percentage:.1f}%)", width=80),
                ft.ProgressBar(value=percentage / 100, width=200, color=ft.colors.BLUE),
            ], alignment=ft.MainAxisAlignment.START)

            category_container.controls.append(category_row)

        page.update()

    summary_period_dropdown.on_change = lambda _: update_dashboard()

    dashboard_view = ft.Column([
        ft.Container(height=20),
        ft.Text("Financial Summary", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),
        summary_period_dropdown,
        ft.Container(height=20),
        income_text,
        expenses_text,
        balance_text,
        ft.Divider(),
        category_container,
    ], scroll=ft.ScrollMode.AUTO)

    # ---- ADD INCOME TAB ----
    income_amount_field = ft.TextField(
        label="Amount ($)",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        prefix_text="$",
    )

    income_source_field = ft.TextField(
        label="Source (e.g., Salary, Freelancing)",
        width=300,
    )

    income_date_field = ft.TextField(
        label="Date (YYYY-MM-DD)",
        value=datetime.datetime.now().strftime("%Y-%m-%d"),
        width=300,
    )

    income_status_text = ft.Text("", color=ft.colors.GREEN)

    def add_income_clicked(_):
        try:
            amount = float(income_amount_field.value)
            source = income_source_field.value
            date = income_date_field.value

            if not source:
                income_status_text.value = "Please enter a source"
                income_status_text.color = ft.colors.RED
            elif amount <= 0:
                income_status_text.value = "Amount must be greater than zero"
                income_status_text.color = ft.colors.RED
            else:
                budget.add_income(amount, source, date)
                income_status_text.value = f"Income of ${amount:.2f} added successfully!"
                income_status_text.color = ft.colors.GREEN

                # Clear fields
                income_amount_field.value = ""
                income_source_field.value = ""
                income_date_field.value = datetime.datetime.now().strftime("%Y-%m-%d")

                # Update dashboard
                update_dashboard()
                update_transactions()
        except ValueError:
            income_status_text.value = "Invalid amount. Please enter a number."
            income_status_text.color = ft.colors.RED

        page.update()

    add_income_button = ft.ElevatedButton(
        "Add Income",
        on_click=add_income_clicked,
        bgcolor=ft.colors.GREEN,
        color=ft.colors.WHITE,
    )

    add_income_view = ft.Column([
        ft.Container(height=20),
        ft.Text("Add New Income", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(height=20),
        income_amount_field,
        income_source_field,
        income_date_field,
        ft.Container(height=10),
        add_income_button,
        income_status_text,
    ])

    # ---- ADD EXPENSE TAB ----
    expense_amount_field = ft.TextField(
        label="Amount ($)",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        prefix_text="$",
    )

    expense_category_dropdown = ft.Dropdown(
        label="Category",
        options=[ft.dropdown.Option(cat) for cat in sorted(budget.categories)],
        width=300,
    )

    expense_description_field = ft.TextField(
        label="Description",
        width=300,
    )

    expense_date_field = ft.TextField(
        label="Date (YYYY-MM-DD)",
        value=datetime.datetime.now().strftime("%Y-%m-%d"),
        width=300,
    )

    expense_status_text = ft.Text("", color=ft.colors.GREEN)

    def add_expense_clicked(_):
        try:
            amount = float(expense_amount_field.value)
            category = expense_category_dropdown.value
            description = expense_description_field.value
            date = expense_date_field.value

            if not category:
                expense_status_text.value = "Please select a category"
                expense_status_text.color = ft.colors.RED
            elif not description:
                expense_status_text.value = "Please enter a description"
                expense_status_text.color = ft.colors.RED
            elif amount <= 0:
                expense_status_text.value = "Amount must be greater than zero"
                expense_status_text.color = ft.colors.RED
            else:
                budget.add_expense(amount, category, description, date)
                expense_status_text.value = f"Expense of ${amount:.2f} added successfully!"
                expense_status_text.color = ft.colors.GREEN

                # Clear fields
                expense_amount_field.value = ""
                expense_category_dropdown.value = ""
                expense_description_field.value = ""
                expense_date_field.value = datetime.datetime.now().strftime("%Y-%m-%d")

                # Update dashboard
                update_dashboard()
                update_transactions()
        except ValueError:
            expense_status_text.value = "Invalid amount. Please enter a number."
            expense_status_text.color = ft.colors.RED

        page.update()

    add_expense_button = ft.ElevatedButton(
        "Add Expense",
        on_click=add_expense_clicked,
        bgcolor=ft.colors.RED,
        color=ft.colors.WHITE,
    )

    add_expense_view = ft.Column([
        ft.Container(height=20),
        ft.Text("Add New Expense", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(height=20),
        expense_amount_field,
        expense_category_dropdown,
        expense_description_field,
        expense_date_field,
        ft.Container(height=10),
        add_expense_button,
        expense_status_text,
    ])

    # ---- TRANSACTIONS TAB ----
    transactions_dropdown = ft.Dropdown(
        label="Transaction Type",
        options=[
            ft.dropdown.Option("all", "All Transactions"),
            ft.dropdown.Option("income", "Income Only"),
            ft.dropdown.Option("expenses", "Expenses Only"),
        ],
        value="all",
        width=200,
    )

    transactions_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Amount")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Description")),
        ],
        border=ft.border.all(1, ft.colors.GREY_400),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        column_spacing=5,
    )

    def update_transactions():
        # Get transactions
        transactions = budget.get_transactions(
            transaction_type=transactions_dropdown.value,
            limit=20
        )

        # Clear table
        transactions_table.rows.clear()

        # Add rows
        for transaction in transactions:
            color = ft.colors.GREEN if transaction["type"] == "Income" else ft.colors.RED

            transactions_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(transaction["type"], color=color)),
                        ft.DataCell(ft.Text(transaction["date"])),
                        ft.DataCell(ft.Text(f"${transaction['amount']:.2f}", color=color)),
                        ft.DataCell(ft.Text(transaction["category"])),
                        ft.DataCell(ft.Text(transaction["description"])),
                    ]
                )
            )

        page.update()

    transactions_dropdown.on_change = lambda _: update_transactions()

    transactions_view = ft.Column([
        ft.Container(height=20),
        ft.Text("Recent Transactions", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),
        transactions_dropdown,
        ft.Container(height=20),
        transactions_table,
    ], scroll=ft.ScrollMode.AUTO)

    # ---- ADVICE TAB ----
    advice_container = ft.Column(spacing=10)

    def update_advice():
        advice_list = budget.get_spending_advice()

        # Clear container
        advice_container.controls.clear()

        # Add advice items
        for advice in advice_list:
            advice_container.controls.append(
                ft.Container(
                    content=ft.Text(advice, size=16),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.BLUE_50,
                )
            )

        page.update()

    advice_view = ft.Column([
        ft.Container(height=20),
        ft.Text("Spending Advice", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(height=20),
        ft.ElevatedButton("Refresh Advice", on_click=lambda _: update_advice()),
        ft.Container(height=10),
        advice_container,
    ])

    # Create the tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text=tab_titles[0],
                content=dashboard_view,
                icon=ft.icons.DASHBOARD,
            ),
            ft.Tab(
                text=tab_titles[1],
                content=add_income_view,
                icon=ft.icons.ARROW_UPWARD,
            ),
            ft.Tab(
                text=tab_titles[2],
                content=add_expense_view,
                icon=ft.icons.ARROW_DOWNWARD,
            ),
            ft.Tab(
                text=tab_titles[3],
                content=transactions_view,
                icon=ft.icons.LIST_ALT,
            ),
            ft.Tab(
                text=tab_titles[4],
                content=advice_view,
                icon=ft.icons.LIGHTBULB_OUTLINE,
            ),
        ],
        expand=1,
    )

    # Add tabs to page
    page.add(tabs)

    # Initial data loading
    update_dashboard()
    update_transactions()
    update_advice()


if __name__ == "__main__":
    ft.app(target=main)