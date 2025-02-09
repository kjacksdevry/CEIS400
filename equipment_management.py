# equipment_management.py

from abc import ABC, abstractmethod

# Importing ABC and abstractmethod to create an abstract base class

# Abstract base class for users (Employees and Supervisors)
class IUser(ABC):
    def __init__(self, user_id, name):
        # Initialize user with an ID and name
        self.user_id = user_id
        self.name = name
    
    @abstractmethod
    def display_info(self):
        # Abstract method to be implemented by subclasses
        pass

# Employee class representing an employee with a skill set
class Employee(IUser):
    def __init__(self, user_id, name, skill_set):
        # Initialize employee with an ID, name, and skill set
        super().__init__(user_id, name)
        self.skill_set = skill_set
    
    # Method for checking out equipment
    def check_out_equipment(self, equipment):
        # Verify if the employee has the required skill to check out the equipment
        if SkillVerification.verify_skill(self, equipment):
            EquipmentCheckout.log_checkout(self, equipment)
        else:
            # Send an alert if the employee is not authorized
            NotificationSystem.send_alert(f"Unauthorized checkout attempt by {self.name}")
    
    # Method for returning equipment
    def return_equipment(self, equipment):
        # Log the return of the equipment
        EquipmentCheckout.log_return(self, equipment)
    
    # Displays employee information
    def display_info(self):
        return f"Employee: {self.name}, Skills: {self.skill_set}"

# Supervisor class representing a supervisor who can generate reports
class Supervisor(IUser):
    def __init__(self, user_id, name):
        # Initialize supervisor with an ID and name
        super().__init__(user_id, name)
    
    # Method for generating an equipment report
    def generate_report(self):
        return ReportGeneration.generate_report()
    
    # Displays supervisor information
    def display_info(self):
        return f"Supervisor: {self.name}"

# Equipment class representing an equipment item
class Equipment:
    def __init__(self, equipment_id, name, status="Available"):
        # Initialize equipment with an ID, name, and default status
        self.equipment_id = equipment_id
        self.name = name
        self.status = status
    
    # Placeholder for barcode scanning functionality
    def scan_barcode(self):
        pass  
    
    # Updates the status of the equipment
    def update_status(self, new_status):
        self.status = new_status

# Singleton Buffer class for tracking checked-out equipment per employee
class Buffer:
    _instances = {}  # Dictionary to store single instances per employee
    
    def __new__(cls, employee_id):
        # Ensure only one buffer instance per employee
        if employee_id not in cls._instances:
            cls._instances[employee_id] = super(Buffer, cls).__new__(cls)
        return cls._instances[employee_id]
    
    def __init__(self, employee_id):
        self.employee_id = employee_id
        self.equipment_list = []
    
    # Adds equipment to the buffer
    def add_equipment(self, equipment):
        self.equipment_list.append(equipment)
    
    # Removes equipment from the buffer
    def remove_equipment(self, equipment):
        self.equipment_list.remove(equipment)

# Skill Verification Module checks if an employee has the required skills
class SkillVerification:
    @staticmethod
    def verify_skill(employee, equipment):
        # Check if the employee has the required skill for the equipment
        return equipment.name in employee.skill_set

# Equipment Checkout Module handles logging checkouts and returns
class EquipmentCheckout:
    @staticmethod
    def log_checkout(employee, equipment):
        # Log when an employee checks out equipment
        print(f"{employee.name} checked out {equipment.name}")
        equipment.update_status("Checked Out")
    
    @staticmethod
    def log_return(employee, equipment):
        # Log when an employee returns equipment
        print(f"{employee.name} returned {equipment.name}")
        equipment.update_status("Available")

# Observer Pattern: Notification System for alerting supervisors
class NotificationSystem:
    observers = []  # List to store subscribed supervisors
    
    @staticmethod
    def subscribe(observer):
        # Subscribe a supervisor to receive notifications
        NotificationSystem.observers.append(observer)
    
    @staticmethod
    def send_alert(message):
        # Send an alert to all subscribed supervisors
        for observer in NotificationSystem.observers:
            print(f"Alert sent to {observer.name}: {message}")

# Report Generation Module for generating reports on equipment usage
class ReportGeneration:
    @staticmethod
    def generate_report():
        return "Generating Equipment Report..."

# Command-line interface for the Equipment Management System
if __name__ == "__main__":
    # Create instances of Employee, Supervisor, and Equipment
    emp = Employee(1, "John Doe", ["Forklift", "Drill"])
    sup = Supervisor(2, "Jane Smith")
    equip = Equipment(101, "Power Drill")
    buf = Buffer(emp.user_id)  # Create buffer for the employee
    NotificationSystem.subscribe(sup)  # Subscribe supervisor for alerts
    
    # Command-line menu loop
    while True:
        print("\nEquipment Management System")
        print("1. Check Out Equipment")
        print("2. Return Equipment")
        print("3. Generate Report")
        print("4. Exit")
        choice = input("Select an option: ")
        
        if choice == "1":
            emp.check_out_equipment(equip)  # Employee checks out equipment
        elif choice == "2":
            emp.return_equipment(equip)  # Employee returns equipment
        elif choice == "3":
            print(sup.generate_report())  # Supervisor generates a report
        elif choice == "4":
            print("Exiting...")
            break  # Exit the program
        else:
            print("Invalid choice. Please try again.")
