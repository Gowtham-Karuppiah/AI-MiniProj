import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from fpdf import FPDF
import webbrowser
import random

# ----------- PDF Creator Class ------------
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Exam Seating Arrangement', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def add_room_table(self, room_number, seating_chart, staff_schedule):
        self.add_page()
        self.chapter_title(f"Room {room_number}")
        
        # Print staff schedule
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Invigilation Schedule', 0, 1, 'L')
        self.set_font('Arial', '', 11)
        for hour, staff in staff_schedule.items():
            self.cell(0, 10, f"Hour {hour}: {staff}", 0, 1)

        # Create seating chart
        self.ln(5)
        self.set_font('Arial', 'B', 11)
        self.cell(30, 10, '', 0)  # Offset for aesthetics
        for bench in range(1, 21):  # Assuming 20 benches
            self.cell(30, 10, f'Bench {bench}', 1, 0, 'C')
        self.ln()

        # Fill benches
        self.set_font('Arial', '', 11)
        for i in range(0, len(seating_chart), 3):
            for j in range(3):
                if i + j < len(seating_chart):
                    self.cell(30, 10, seating_chart[i + j], 1, 0, 'C')
                else:
                    self.cell(30, 10, '', 1, 0, 'C')
            self.ln()  # New line after each bench row

# ------------- GUI App Class ----------------
class ExamSeatingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Seating Arrangement System")
        self.style = tb.Style(theme="flatly")
        self.frame = tb.Frame(self.root, padding=20)
        self.frame.pack(fill=BOTH, expand=True)

        # Variables
        self.rooms = tk.IntVar()
        self.subject_entries = []
        self.staff_entries = []
        self.subject_data = {}

        # Title
        tb.Label(self.frame, text="Exam Seating System", font=("Arial", 24)).pack(pady=10)

        # Room Input
        tb.Label(self.frame, text="Enter number of rooms available:", font=("Arial", 14)).pack(pady=5)
        tb.Entry(self.frame, textvariable=self.rooms, font=("Arial", 12)).pack()

        # Subject Section
        tb.Label(self.frame, text="Subjects and Student Ranges", font=("Arial", 16)).pack(pady=10)
        self.subject_frame = tb.Frame(self.frame)
        self.subject_frame.pack()
        tb.Button(self.frame, text="Add Subject", command=self.add_subject, bootstyle="success").pack(pady=5)

        # Staff Section
        tb.Label(self.frame, text="Staff Details", font=("Arial", 16)).pack(pady=10)
        self.staff_frame = tb.Frame(self.frame)
        self.staff_frame.pack()
        tb.Button(self.frame, text="Add Staff", command=self.add_staff, bootstyle="success").pack(pady=5)

        # Submit Button
        tb.Button(self.frame, text="Generate Seating", command=self.generate_seating, bootstyle="primary").pack(pady=20)

    def add_subject(self):
        frame = tb.Frame(self.subject_frame)
        frame.pack(pady=2)
        code_var = tk.StringVar()
        start_var = tk.StringVar()
        end_var = tk.StringVar()
        tb.Entry(frame, textvariable=code_var, width=10).pack(side=LEFT, padx=5)
        tb.Entry(frame, textvariable=start_var, width=10).pack(side=LEFT, padx=5)
        tb.Entry(frame, textvariable=end_var, width=10).pack(side=LEFT, padx=5)
        self.subject_entries.append((code_var, start_var, end_var))

    def add_staff(self):
        frame = tb.Frame(self.staff_frame)
        frame.pack(pady=2)
        name_var = tk.StringVar()
        tb.Entry(frame, textvariable=name_var, width=20).pack(side=LEFT, padx=5)
        self.staff_entries.append(name_var)

    def generate_seating(self):
        room_count = self.rooms.get()
        if room_count <= 0:
            messagebox.showerror("Error", "Please enter a valid number of rooms!")
            return

        self.subject_data.clear()
        for code_var, start_var, end_var in self.subject_entries:
            code = code_var.get()
            start = start_var.get()
            end = end_var.get()
            if code and start and end:
                self.subject_data[code] = (int(start), int(end))

        staff_names = [s.get() for s in self.staff_entries if s.get()]
        if not staff_names:
            messagebox.showerror("Error", "Please enter staff details properly!")
            return

        # Generate student list
        students = []
        for subject, (start, end) in self.subject_data.items():
            for num in range(start, end + 1):
                roll = f"{subject}{num:03d}"  # Format roll number
                students.append((roll, subject))

        # Generate seating arrangement
        arrangement = self.generate_seating_arrangement(students, room_count)

        # Shuffle staff for each hour and create invigilation schedule
        staff_schedule = self.create_staff_schedule(staff_names, 3)  # 3 hours

        # Create PDF output with seating arrangement and staff schedule
        pdf = PDF()
        for room_number in range(1, room_count + 1):
            seating_chart = arrangement.get(room_number, [])
            pdf.add_room_table(room_number, seating_chart, staff_schedule[room_number])

        # Save and open the PDF
        pdf_file = 'ExamSeatingChart.pdf'
        pdf.output(pdf_file)
        webbrowser.open(pdf_file)  # Optional: auto open PDF
        messagebox.showinfo("Success", "Seating Generated! PDF saved as 'ExamSeatingChart.pdf'.")

    def generate_seating_arrangement(self, students, room_count):
        # Sort students by roll number
        students.sort(key=lambda x: x[0])  # Sort by roll number

        arrangement = {i: [] for i in range(1, room_count + 1)}
        max_students_per_room = 60  # Total seats in each room (20 benches * 3 seats per bench)

        # Create a subject-based grouping mechanism
        subjects = {}
        for student in students:
            subject = student[0][:-3]  # Extract subject code from roll number
            if subject not in subjects:
                subjects[subject] = []
            subjects[subject].append(student[0])  # Store roll number

        # Start filling the arrangement for each room uniquely
        for room_number in range(1, room_count + 1):
            available_students = [student for student_list in subjects.values() for student in student_list]

            idx = 0
            while idx < max_students_per_room :
                if not available_students:
                    arrangement[room_number].append(" ")
                    idx+=1
                    available_students = [student for student_list in subjects.values() for student in student_list]
                    continue
                chosen = available_students.pop(0)

                # Ensure no two same subjects are seated next to each other
                if (arrangement[room_number] and
                    (chosen[:-3] == arrangement[room_number][-1][:-3] or  # Same subject as last added
                     len(arrangement[room_number]) % 3 == 0 and
                     chosen[:-3] == arrangement[room_number][-3][:-3])):  # Same subject as first seat in current bench

                    # if available_students:  # Try next available student
                    #     available_students.append(chosen)  # Put back the chosen student
                    continue  # Re-attempt without incrementing idx
                else:
                    arrangement[room_number].append(chosen)

                    # Remove the chosen student from the master subject group to prevent overlap in next rooms
                    for subject in subjects.keys():
                        if chosen in subjects[subject]:
                            subjects[subject].remove(chosen)

                    idx += 1

        return arrangement

    def create_staff_schedule(self, staff_names, hours):
        staff_schedule = {}
        for hour in range(1, hours + 1):
            random_staff = random.sample(staff_names, len(staff_names))  # Shuffle staff for each hour
            for room_number in range(1, self.rooms.get() + 1):
                staff_assignment = random_staff[(room_number - 1) % len(random_staff)]
                if room_number not in staff_schedule:
                    staff_schedule[room_number] = {}
                staff_schedule[room_number][hour] = staff_assignment
        return staff_schedule

# --------------- Main Program -----------------
if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = ExamSeatingApp(root)
    root.mainloop()
