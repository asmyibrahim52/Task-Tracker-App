##Task Tracker (Python + PyQt5)

A clean, full-featured To-Do List Manager built with Python and PyQt5.  
This desktop app lets you create, organize, and track tasks with deadlines, reminders, priorities, and automatic data saving.

## Demo
<img width="1512" height="982" alt="Screenshot 2025-10-24 at 06 29 17" src="https://github.com/user-attachments/assets/1a14e345-8b21-476e-86da-5d74ae591d3b" />
<img width="1512" height="982" alt="Screenshot 2025-10-24 at 06 30 28" src="https://github.com/user-attachments/assets/1cc19b62-fdab-403b-b3d3-8c4b10956097" />
<img width="1512" height="982" alt="Screenshot 2025-10-24 at 06 30 40" src="https://github.com/user-attachments/assets/fe1d06c5-9293-4da3-a788-9260b65247fb" />


## Features

- Add, edit, and delete tasks with detailed descriptions  
- Set task deadlines (date + time)  
- Optional notifications before deadlines  
- 🟥🟨🟩 Priority levels (High, Medium, Low) with color coding  
- Overdue task detection  
- Mark tasks complete or incomplete  
- Filter by priority, overdue, or completion status  
- Automatically saves all tasks to a local `tasks.json` file  
- Responsive PyQt5 interface


## Skills & Technologies Used

- Python 
- PyQt5 – GUI framework  
- QTimer – background checks for deadlines & reminders  
- JSON – persistent data storage  
- datetime – for scheduling & notifications  
- OOP (Object-Oriented Programming) – clean, modular structure  

---

## Installation & Setup

1️⃣ Clone this repository

git clone [https://github.com/YourUsername/TodoApp.git](https://github.com/asmyibrahim52/Task-Tracker-App)


2️⃣ (Optional) Create and activate a virtual environment

python3 -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows


3️⃣ Install dependencies

pip install PyQt5

4️⃣ Run the application

python main.py


# Project Structure

📂 TodoApp/
├── main.py              # Main application script
├── tasks.json           # Auto-generated file storing tasks
├── screenshots/         # Demo images or GIFs
└── README.md            # Project documentation


---

# Example Screenshots

Task List| <img width="1512" height="982" alt="Screenshot 2025-10-24 at 06 50 13" src="https://github.com/user-attachments/assets/10de71e6-1d06-42b6-8a48-4775efbf57b7" />
Add/Edit Dialog| <img width="1512" height="982" alt="Screenshot 2025-10-24 at 06 50 33" src="https://github.com/user-attachments/assets/9a7cb859-dd47-4e94-a113-aca068590778" />
Reminder Popup| <img width="1512" height="982" alt="Screenshot 2025-10-24 at 06 56 00" src="https://github.com/user-attachments/assets/43d0cd0e-8b57-42b4-ae29-e4abe250540f" />



# How It Works

1. Click 'Add Task' to create a new task.
2. Enter the title, description, priority, deadline, and optional notification.
3. The app refreshes every minute to:

   * Warn about upcoming deadlines ⏰
   * Highlight overdue tasks ⚠️
4. Tasks are saved automatically to `tasks.json`, ensuring persistence between sessions.

---

# Future Enhancements

* Add dark mode support
* Cloud synchronization or multi-device support
* Export task data to CSV/PDF
* Add recurring tasks


# Author

**Asmau Ibrahim**
[GitHub](https://github.com/asmyibrahim52)
[LinkedIn] (https://www.linkedin.com/in/asmau-ibrahim-/)

> Passionate about building useful, elegant desktop apps with Python and PyQt.


# Acknowledgments

* Built as part of a personal learning project to improve PyQt5 GUI development.
* Inspired by minimalistic task management tools with a focus on usability and design.

