import os
import time
import math
os.environ['TERM'] = 'xterm'

class BudgetPlanner:
    def __init__(self):
        self.income = 0
        self.expenses = {}
        self.savings = {}
        self.investments = {}
        self.savings_goals = {}

    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def add_income(self):
        """Add income details."""
        self.clear_screen()
        print("=== ADD INCOME ===")
        while True:
            try:
                self.income = float(input("Enter your monthly income: $"))
                if self.income <= 0:
                    print("Income must be a positive number.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

    def add_expenses(self):
        """Add and track monthly expenses."""
        self.clear_screen()
        print("=== ADD EXPENSES ===")
        while True:
            category = input("Enter expense category (or 'done' to finish): ").strip()
            if category.lower() == 'done':
                break

            while True:
                try:
                    amount = float(input(f"Enter amount for {category}: $"))
                    if amount < 0:
                        print("Expense amount cannot be negative.")
                        continue
                    self.expenses[category] = amount
                    break
                except ValueError:
                    print("Please enter a valid number.")

    def investment_projection(self):
        """Investment growth projection menu."""
        self.clear_screen()
        print("=== INVESTMENT GROWTH PROJECTION ===")

        while True:
            try:
                principal = float(input("Enter initial investment amount: $"))
                annual_rate = float(input("Enter annual interest rate (e.g., 0.05 for 5%): "))
                years = int(input("Enter number of years to project: "))

                future_value = self.calculate_investment_growth(principal, annual_rate, years)

                print(f"\nInitial Investment: ${principal:.2f}")
                print(f"Annual Interest Rate: {annual_rate * 100:.2f}%")
                print(f"Investment Period: {years} years")
                print(f"Projected Future Value: ${future_value:.2f}")
                print(f"Total Growth: ${future_value - principal:.2f}")

                input("\nPress Enter to continue...")
                break
            except ValueError:
                print("Please enter valid numbers.")

    def calculate_investment_growth(self, principal, annual_rate, years):
        """
        Calculate future value using compound interest formula:
        Future Value = Principal * (1 + Annual Interest Rate)^(Number of Years)

        Args:
            principal (float): Initial investment amount
            annual_rate (float): Annual interest rate (in decimal)
            years (int): Number of years to invest

        Returns:
            float: Future value of the investment
        """
        future_value = principal * ((1 + annual_rate) ** years)
        return future_value

    def calculate_required_monthly_investment(self, target_amount, years, annual_rate):
        """
        Calculate monthly investment required to reach a savings goal.

        Args:
            target_amount (float): Savings goal amount
            years (int): Number of years to reach the goal
            annual_rate (float): Annual interest rate (in decimal)

        Returns:
            float: Required monthly investment
        """
        # Number of compounding periods per year
        n = 12  # monthly compounding

        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / 12

        # Total number of compounding periods
        total_periods = years * n

        # Calculate required monthly investment using future value of series formula
        # FV = PMT * ((1 + r)^n - 1) / r
        # Rearranged to solve for PMT (monthly payment)
        if monthly_rate == 0:
            # If interest rate is 0, simple division
            monthly_investment = target_amount / (years * 12)
        else:
            monthly_investment = target_amount / (((1 + monthly_rate) ** total_periods - 1) / monthly_rate)

        return monthly_investment

    def add_savings_goal(self):
        """Add and manage savings goals."""
        self.clear_screen()
        print("=== SAVINGS GOAL TRACKER ===")

        while True:
            goal_name = input("Enter savings goal name (or 'done' to finish): ").strip()
            if goal_name.lower() == 'done':
                break

            while True:
                try:
                    target_amount = float(input("Enter target amount for this goal: $"))
                    if target_amount <= 0:
                        print("Target amount must be a positive number.")
                        continue

                    years = int(input("How many years to reach this goal? "))
                    if years <= 0:
                        print("Years must be a positive number.")
                        continue

                    annual_rate = float(input("Expected annual interest rate (e.g., 0.05 for 5%): "))

                    # Calculate required monthly investment
                    monthly_investment = self.calculate_required_monthly_investment(
                        target_amount, years, annual_rate
                    )

                    # Store the goal
                    self.savings_goals[goal_name] = {
                        'target_amount': target_amount,
                        'years': years,
                        'annual_rate': annual_rate,
                        'monthly_investment_required': monthly_investment
                    }

                    # Display results
                    print("\n--- Savings Goal Analysis ---")
                    print(f"Goal: {goal_name}")
                    print(f"Target Amount: ${target_amount:.2f}")
                    print(f"Time Frame: {years} years")
                    print(f"Annual Interest Rate: {annual_rate * 100:.2f}%")
                    print(f"Monthly Investment Required: ${monthly_investment:.2f}")

                    # Project final amount
                    total_contributions = monthly_investment * (years * 12)
                    projected_final_amount = self.calculate_investment_growth(
                        monthly_investment * 12,  # Annual initial investment
                        annual_rate,
                        years
                    )

                    print(f"Total Contributions: ${total_contributions:.2f}")
                    print(f"Projected Final Amount: ${projected_final_amount:.2f}")

                    input("\nPress Enter to continue...")
                    break
                except ValueError:
                    print("Please enter valid numbers.")

    def view_savings_goals(self):
        """View and track existing savings goals."""
        self.clear_screen()
        print("=== SAVINGS GOALS OVERVIEW ===")

        if not self.savings_goals:
            print("No savings goals have been set.")
            input("\nPress Enter to continue...")
            return

        for goal_name, goal_details in self.savings_goals.items():
            print(f"\nGoal: {goal_name}")
            print(f"Target Amount: ${goal_details['target_amount']:.2f}")
            print(f"Time Frame: {goal_details['years']} years")
            print(f"Annual Interest Rate: {goal_details['annual_rate'] * 100:.2f}%")
            print(f"Monthly Investment Required: ${goal_details['monthly_investment_required']:.2f}")

        input("\nPress Enter to continue...")

    def budget_summary(self):
        """Display budget summary."""
        self.clear_screen()
        print("=== BUDGET SUMMARY ===")

        # Income
        print(f"Monthly Income: ${self.income:.2f}")

        # Expenses
        total_expenses = sum(self.expenses.values())
        print("\nExpenses:")
        for category, amount in self.expenses.items():
            print(f"{category}: ${amount:.2f}")
        print(f"Total Expenses: ${total_expenses:.2f}")

        # Remaining Budget
        remaining = self.income - total_expenses
        print(f"\nRemaining Budget: ${remaining:.2f}")

        input("\nPress Enter to continue...")

    def main_menu(self):
        """Main menu of the budget planner."""
        while True:
            self.clear_screen()
            print("=== BUDGET PLANNER ===")
            print("1. Add Income")
            print("2. Add Expenses")
            print("3. Investment Growth Projection")
            print("4. Budget Summary")
            print("5. Add Savings Goal")
            print("6. View Savings Goals")
            print("7. Exit")

            choice = input("Enter your choice (1-7): ")

            if choice == '1':
                self.add_income()
            elif choice == '2':
                self.add_expenses()
            elif choice == '3':
                self.investment_projection()
            elif choice == '4':
                self.budget_summary()
            elif choice == '5':
                self.add_savings_goal()
            elif choice == '6':
                self.view_savings_goals()
            elif choice == '7':
                print("Thank you for using the Budget Planner!")
                break
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)


def main():
    budget_planner = BudgetPlanner()
    budget_planner.main_menu()


if __name__ == "__main__":
    main()