import sqlite3

class Database:
    def __init__(self, db_name="equipment.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.load_equipment_from_file()  # Load equipment on startup
        self.load_employees_from_file()  # Load employees on startup

    def create_tables(self):
        """Create database tables if they do not exist."""
        with self.conn:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT,
                                    skill_set TEXT)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS equipment (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT,
                                    required_skills TEXT,
                                    status TEXT DEFAULT 'Available')''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS checkouts (
                                    id INTEGER PRIMARY KEY,
                                    employee_id INTEGER,
                                    equipment_id INTEGER,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (employee_id) REFERENCES employees(id),
                                    FOREIGN KEY (equipment_id) REFERENCES equipment(id))''')

    def add_employee(self, employee_id, name, skill_set):
        """Add an employee to the database."""
        with self.conn:
            try:
                self.cursor.execute("INSERT INTO employees (id, name, skill_set) VALUES (?, ?, ?)", 
                                    (employee_id, name, skill_set))
            except sqlite3.IntegrityError:
                print(f"Employee ID {employee_id} already exists. Skipping entry.")

    def add_equipment(self, equipment_id, name, required_skills):
        """Add equipment to the database."""
        with self.conn:
            try:
                self.cursor.execute("INSERT INTO equipment (id, name, required_skills) VALUES (?, ?, ?)", 
                                    (equipment_id, name, required_skills))
            except sqlite3.IntegrityError:
                print(f"Equipment ID {equipment_id} already exists. Skipping entry.")

    def load_equipment_from_file(self, filename="equipment_data.txt"):
        """Load equipment data from a file and insert into the database, avoiding duplicates."""
        try:
            with open(filename, "r") as file:
                for line in file:
                    parts = line.strip().split(", ")
                    if len(parts) == 3 and parts[0].isdigit():
                        equipment_id, name, required_skills = parts
                        self.cursor.execute("SELECT id FROM equipment WHERE id = ?", (int(equipment_id),))
                        existing = self.cursor.fetchone()
                        if not existing:
                            self.add_equipment(int(equipment_id), name, required_skills)
                        else:
                            print(f"Skipping duplicate equipment ID {equipment_id} ({name}). Already exists.")
            print("Equipment data loaded successfully!")
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Equipment data not loaded.")

    def load_employees_from_file(self, filename="employees_data.txt"):
        """Load employees from a file and insert into the database, avoiding duplicates."""
        try:
            with open(filename, "r") as file:
                for line in file:
                    parts = line.strip().split(", ")
                    if len(parts) >= 3 and parts[0].isdigit():
                        employee_id = int(parts[0])
                        name = parts[1]
                        skills = ", ".join(parts[2:])
                        self.cursor.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
                        existing = self.cursor.fetchone()
                        if not existing:
                            self.add_employee(employee_id, name, skills)
                        else:
                            print(f"Skipping duplicate employee ID {employee_id} ({name}). Already exists.")
            print("Employee data loaded successfully!")
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Employee data not loaded.")

    def check_out_equipment(self, employee_id, equipment_id):
        """Log an equipment checkout event."""
        with self.conn:
            try:
                self.cursor.execute("SELECT name, skill_set FROM employees WHERE id = ?", (employee_id,))
                employee_data = self.cursor.fetchone()
                if not employee_data:
                    return "Employee ID not found."

                employee_name, employee_skills = employee_data
                employee_skills = employee_skills.split(", ")

                self.cursor.execute("SELECT name, required_skills, status FROM equipment WHERE id = ?", (equipment_id,))
                equipment_data = self.cursor.fetchone()
                if not equipment_data:
                    return "Equipment ID not found."

                equipment_name, required_skills, status = equipment_data
                required_skills = required_skills.split(", ")

                if not any(skill in employee_skills for skill in required_skills):
                    return f"Error: {employee_name} does not have the required skills ({', '.join(required_skills)}) to check out {equipment_name}."

                if status == "Checked Out":
                    return "Equipment is already checked out."

                self.cursor.execute("INSERT INTO checkouts (employee_id, equipment_id) VALUES (?, ?)", 
                                    (employee_id, equipment_id))
                self.cursor.execute("UPDATE equipment SET status = 'Checked Out' WHERE id = ?", (equipment_id,))
                return f"{employee_name} successfully checked out {equipment_name}."
            except sqlite3.Error as e:
                self.conn.rollback()
                return f"Database error: {e}"

    def return_equipment(self, equipment_id):
        """Log an equipment return event."""
        with self.conn:
            try:
                self.cursor.execute("SELECT status FROM equipment WHERE id = ?", (equipment_id,))
                status = self.cursor.fetchone()
                
                if not status:
                    return "Equipment ID not found."

                if status[0] == "Checked Out":
                    self.cursor.execute("UPDATE equipment SET status = 'Available' WHERE id = ?", (equipment_id,))
                    return "Equipment returned successfully."
                else:
                    return "This equipment was not checked out."
            except sqlite3.Error as e:
                self.conn.rollback()
                return f"Database error: {e}"

    def get_employee_skills(self, employee_id):
        """Fetch employee skill set."""
        with self.conn:
            try:
                self.cursor.execute("SELECT skill_set FROM employees WHERE id = ?", (employee_id,))
                result = self.cursor.fetchone()
                return result[0] if result else None
            except sqlite3.Error as e:
                return f"Database error: {e}"

    def close(self):
        """Close the database connection."""
        self.conn.close()

# Example usage
if __name__ == "__main__":
    db = Database()  # Equipment and employees load automatically
