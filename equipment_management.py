# equipment_management.py

from abc import ABC, abstractmethod
from database import Database  

db = Database()  

# Abstract base class for users (Employees and Supervisors)
class IUser(ABC):
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
    
    @abstractmethod
    def display_info(self):
        pass

# Employee class representing an employee with a skill set
class Employee(IUser):
    def __init__(self, user_id, name, skill_set):
        super().__init__(user_id, name)
        self.skill_set = skill_set
    
    def check_out_equipment(self, equipment_id):
        # Ensure employee has the required skill to use the equipment
        db.cursor.execute("SELECT name FROM equipment WHERE id = ?", (equipment_id,))
        equipment = db.cursor.fetchone()
        
        if not equipment:
            print("Invalid Equipment ID.")
            return
        
        equipment_name = equipment[0]
        if equipment_name not in self.skill_set:
            print(f"Error: {self.name} does not have the required skills to check out {equipment_name}.")
            return
        
        # Ensure equipment is not already checked out
        db.cursor.execute("SELECT status FROM equipment WHERE id = ?", (equipment_id,))
        status = db.cursor.fetchone()
        if status and status[0] == "Checked Out":
            print("This equipment is already checked out and must be returned before another employee can check it out.")
        else:
            result = db.check_out_equipment(self.user_id, equipment_id)
            print(result)

    def return_equipment(self, equipment_id):
        # Ensure equipment is actually checked out before returning
        db.cursor.execute("SELECT status FROM equipment WHERE id = ?", (equipment_id,))
        status = db.cursor.fetchone()
        if status and status[0] == "Available":
            print("This equipment was not checked out.")
        else:
            result = db.return_equipment(equipment_id)
            print(result)

    def display_info(self):
        return f"Employee: {self.name}, Skills: {self.skill_set}"

# Supervisor class representing a supervisor who can generate reports
class Supervisor(IUser):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)
    
    def generate_report(self):
        return ReportGeneration.generate_report()
    
    def display_info(self):
        return f"Supervisor: {self.name}"

# Skill Verification Module checks if an employee has the required skills
class SkillVerification:
    @staticmethod
    def verify_skill(employee, equipment_name):
        return equipment_name in employee.skill_set

# Observer Pattern: Notification System for alerting supervisors
class NotificationSystem:
    observers = []
    
    @staticmethod
    def subscribe(observer):
        NotificationSystem.observers.append(observer)
    
    @staticmethod
    def send_alert(message):
        for observer in NotificationSystem.observers:
            print(f"Alert sent to {observer.name}: {message}")

# Report Generation Module for generating reports on equipment usage
class ReportGeneration:
    @staticmethod
    def generate_report():
        db.cursor.execute("SELECT DISTINCT employees.name, equipment.name FROM checkouts "
                          "JOIN employees ON checkouts.employee_id = employees.id "
                          "JOIN equipment ON checkouts.equipment_id = equipment.id "
                          "WHERE equipment.status = 'Checked Out'")
        report_data = db.cursor.fetchall()
        
        if report_data:
            print("\nChecked-Out Equipment Report:")
            seen_entries = set()
            for entry in report_data:
                if entry not in seen_entries:
                    seen_entries.add(entry)
                    print(f"Employee: {entry[0]} - Equipment: {entry[1]}")
        else:
            print("\nNo equipment is currently checked out.")

# Command-line interface for the Equipment Management System
try:
    while True:
        print("\nEquipment Management System")
        print("1. Check Out Equipment")
        print("2. Return Equipment")
        print("3. Generate Report")
        print("4. List Employees and Equipment")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            try:
                emp_id = int(input("Enter Employee ID: "))
                equip_id = int(input("Enter Equipment ID: "))
                db.cursor.execute("SELECT name, skill_set FROM employees WHERE id = ?", (emp_id,))
                employee_data = db.cursor.fetchone()
                if employee_data:
                    emp = Employee(emp_id, employee_data[0], employee_data[1].split(", "))
                    emp.check_out_equipment(equip_id)
                else:
                    print("Invalid Employee ID.")
            except ValueError:
                print("Invalid input. Please enter numeric IDs.")

        elif choice == "2":
            try:
                equip_id = int(input("Enter Equipment ID to return: "))
                print(db.return_equipment(equip_id))
            except ValueError:
                print("Invalid input. Please enter a valid Equipment ID.")

        elif choice == "3":
            ReportGeneration.generate_report()

        elif choice == "4":
            print("\nEmployees:")
            db.cursor.execute("SELECT * FROM employees")
            employees = db.cursor.fetchall()
            for emp in employees:
                print(f"ID: {emp[0]}, Name: {emp[1]}, Skills: {emp[2]}")
            
            print("\nEquipment:")
            db.cursor.execute("SELECT * FROM equipment")
            equipment = db.cursor.fetchall()
            for equip in equipment:
                print(f"ID: {equip[0]}, Name: {equip[1]}, Status: {equip[2]}")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

finally:
    db.close()  # Ensure the database always closes
