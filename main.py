import sys
import json
import os
from datetime import datetime, date, time, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QTextEdit, 
                             QComboBox, QDateEdit, QTimeEdit, QListWidget, QListWidgetItem,
                             QLabel, QMessageBox, QDialog, QDialogButtonBox,
                             QFormLayout, QGroupBox, QSplitter, QCheckBox)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QFont, QColor


class Task:
    def __init__(self, title="", description="", priority="Medium", deadline=None, deadline_time=None, 
                 notify_enabled=False, notify_before_minutes=30, completed=False):
        self.title = title
        self.description = description
        self.priority = priority
        self.deadline = deadline  # date object
        self.deadline_time = deadline_time  # time object
        self.notify_enabled = notify_enabled
        self.notify_before_minutes = notify_before_minutes
        self.completed = completed
        self.created_at = datetime.now().isoformat()
        self.notified = False  # Track if notification was already sent
    
    def get_deadline_datetime(self):
        """Get the full datetime of the deadline"""
        if self.deadline and self.deadline_time:
            return datetime.combine(self.deadline, self.deadline_time)
        elif self.deadline:
            return datetime.combine(self.deadline, time(23, 59))  # End of day
        return None
    
    def is_overdue(self):
        """Check if the task is overdue"""
        deadline_dt = self.get_deadline_datetime()
        if deadline_dt and not self.completed:
            return datetime.now() > deadline_dt
        return False
    
    def should_notify(self):
        """Check if notification should be sent"""
        if not self.notify_enabled or self.completed or self.notified:
            return False
        
        deadline_dt = self.get_deadline_datetime()
        if not deadline_dt:
            return False
        
        now = datetime.now()
        notification_time = deadline_dt - timedelta(minutes=self.notify_before_minutes)
        return now >= notification_time
    
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'deadline_time': self.deadline_time.isoformat() if self.deadline_time else None,
            'notify_enabled': self.notify_enabled,
            'notify_before_minutes': self.notify_before_minutes,
            'completed': self.completed,
            'created_at': self.created_at,
            'notified': self.notified
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls()
        task.title = data.get('title', '')
        task.description = data.get('description', '')
        task.priority = data.get('priority', 'Medium')
        task.deadline = datetime.fromisoformat(data['deadline']).date() if data.get('deadline') else None
        
        # Handle deadline_time with backward compatibility
        deadline_time_str = data.get('deadline_time')
        if deadline_time_str:
            try:
                # Try parsing as time string first (HH:MM:SS format)
                task.deadline_time = datetime.strptime(deadline_time_str, '%H:%M:%S').time()
            except ValueError:
                try:
                    # Try parsing as datetime isoformat
                    task.deadline_time = datetime.fromisoformat(deadline_time_str).time()
                except ValueError:
                    # If both fail, set to None
                    task.deadline_time = None
        else:
            task.deadline_time = None
        
        task.notify_enabled = data.get('notify_enabled', False)
        task.notify_before_minutes = data.get('notify_before_minutes', 30)
        task.completed = data.get('completed', False)
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.notified = data.get('notified', False)
        return task


class TaskDialog(QDialog):
    def __init__(self, task=None, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Add/Edit Task" if task else "Add Task")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        
        if task:
            self.load_task_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter task title...")
        form_layout.addRow("Title:", self.title_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter task description...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Deadline Date
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setDate(QDate.currentDate())
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setMinimumDate(QDate.currentDate())  # Prevent past dates
        form_layout.addRow("Deadline Date:", self.deadline_edit)
        
        # Deadline Time
        self.deadline_time_edit = QTimeEdit()
        self.deadline_time_edit.setTime(QTime(23, 59))  # Default to end of day
        self.deadline_time_edit.setDisplayFormat("HH:mm")
        form_layout.addRow("Deadline Time:", self.deadline_time_edit)
        
        # Connect date change to update minimum time
        self.deadline_edit.dateChanged.connect(self.update_minimum_time)
        
        # Notification settings
        self.notify_checkbox = QCheckBox("Enable notifications")
        self.notify_checkbox.stateChanged.connect(self.toggle_notification_settings)
        form_layout.addRow("", self.notify_checkbox)
        
        # Notification timing
        self.notify_timing_layout = QHBoxLayout()
        self.notify_before_spinbox = QComboBox()
        self.notify_before_spinbox.addItems([
            "5 minutes", "15 minutes", "30 minutes", "1 hour", 
            "2 hours", "4 hours", "1 day", "2 days", "1 week"
        ])
        self.notify_before_spinbox.setCurrentText("30 minutes")
        self.notify_timing_layout.addWidget(QLabel("Notify"))
        self.notify_timing_layout.addWidget(self.notify_before_spinbox)
        self.notify_timing_layout.addWidget(QLabel("before deadline"))
        self.notify_timing_layout.addStretch()
        
        notify_widget = QWidget()
        notify_widget.setLayout(self.notify_timing_layout)
        form_layout.addRow("", notify_widget)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initially disable notification timing
        self.toggle_notification_settings()
    
    def toggle_notification_settings(self):
        """Enable/disable notification timing controls based on checkbox"""
        enabled = self.notify_checkbox.isChecked()
        self.notify_before_spinbox.setEnabled(enabled)
    
    def update_minimum_time(self, date):
        """Update minimum time when date changes to prevent past deadlines"""
        current_date = QDate.currentDate()
        current_time = QTime.currentTime()
        
        if date == current_date:
            # If today is selected, set minimum time to current time + 1 minute
            min_time = current_time.addSecs(60)  # Add 1 minute buffer
            self.deadline_time_edit.setMinimumTime(min_time)
            
            # If current time is set to a past time, update it
            if self.deadline_time_edit.time() < min_time:
                self.deadline_time_edit.setTime(min_time)
        else:
            # For future dates, no minimum time restriction
            self.deadline_time_edit.setMinimumTime(QTime(0, 0))
    
    def load_task_data(self):
        if self.task:
            self.title_edit.setText(self.task.title)
            self.description_edit.setPlainText(self.task.description)
            self.priority_combo.setCurrentText(self.task.priority)
            
            if self.task.deadline:
                self.deadline_edit.setDate(QDate.fromString(self.task.deadline.isoformat(), Qt.ISODate))
                # For existing tasks, allow past dates (they might have been valid when created)
                self.deadline_edit.setMinimumDate(QDate(1900, 1, 1))  # Very old minimum date
                
            if self.task.deadline_time:
                self.deadline_time_edit.setTime(QTime.fromString(self.task.deadline_time.strftime("%H:%M"), "HH:mm"))
            
            # Load notification settings
            self.notify_checkbox.setChecked(self.task.notify_enabled)
            self.toggle_notification_settings()
            
            # Set notification timing
            timing_map = {
                5: "5 minutes", 15: "15 minutes", 30: "30 minutes", 
                60: "1 hour", 120: "2 hours", 240: "4 hours",
                1440: "1 day", 2880: "2 days", 10080: "1 week"
            }
            reverse_map = {v: k for k, v in timing_map.items()}
            minutes = self.task.notify_before_minutes
            if minutes in timing_map:
                self.notify_before_spinbox.setCurrentText(timing_map[minutes])
            else:
                self.notify_before_spinbox.setCurrentText("30 minutes")
            
            # Update minimum time based on loaded date
            self.update_minimum_time(self.deadline_edit.date())
    
    def get_task_data(self):
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        priority = self.priority_combo.currentText()
        deadline = self.deadline_edit.date().toPyDate()
        deadline_time = self.deadline_time_edit.time().toPyTime()
        
        # Notification settings
        notify_enabled = self.notify_checkbox.isChecked()
        
        # Convert notification timing to minutes
        timing_map = {
            "5 minutes": 5, "15 minutes": 15, "30 minutes": 30,
            "1 hour": 60, "2 hours": 120, "4 hours": 240,
            "1 day": 1440, "2 days": 2880, "1 week": 10080
        }
        notify_before_minutes = timing_map.get(self.notify_before_spinbox.currentText(), 30)
        
        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a task title.")
            return None
        
        # Validate deadline is not in the past
        deadline_datetime = datetime.combine(deadline, deadline_time)
        now = datetime.now()
        
        if deadline_datetime <= now:
            QMessageBox.warning(self, "Invalid Deadline", 
                              "The deadline must be in the future. Please select a future date and time.")
            return None
        
        return {
            'title': title,
            'description': description,
            'priority': priority,
            'deadline': deadline,
            'deadline_time': deadline_time,
            'notify_enabled': notify_enabled,
            'notify_before_minutes': notify_before_minutes
        }


class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.data_file = "tasks.json"
        
        self.setWindowTitle("To-Do List Manager")
        self.setGeometry(100, 100, 800, 600)
        
        self.setup_ui()
        self.load_tasks()
        self.update_task_list()
        
        # Timer to check for overdue tasks and notifications
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_overdue_and_notifications)
        self.timer.start(60000)  # Check every minute
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("To-Do List Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add task button
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(self.add_button)
        
        main_layout.addLayout(header_layout)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Task list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "High Priority", "Medium Priority", "Low Priority", "Overdue", "Completed"])
        self.filter_combo.currentTextChanged.connect(self.update_task_list)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        left_layout.addLayout(filter_layout)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.itemClicked.connect(self.on_task_selected)
        self.task_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        left_layout.addWidget(self.task_list)
        
        # Task actions
        action_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_task)
        self.edit_button.setEnabled(False)
        action_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_task)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        action_layout.addWidget(self.delete_button)
        
        self.toggle_button = QPushButton("Toggle Complete")
        self.toggle_button.clicked.connect(self.toggle_task_completion)
        self.toggle_button.setEnabled(False)
        action_layout.addWidget(self.toggle_button)
        
        left_layout.addLayout(action_layout)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Task details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        details_label = QLabel("Task Details")
        details_font = QFont()
        details_font.setPointSize(14)
        details_font.setBold(True)
        details_label.setFont(details_font)
        right_layout.addWidget(details_label)
        
        # Task details group
        self.details_group = QGroupBox()
        self.details_group.setEnabled(False)
        details_group_layout = QFormLayout(self.details_group)
        
        self.title_label = QLabel("-")
        self.title_label.setWordWrap(True)
        details_group_layout.addRow("Title:", self.title_label)
        
        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        details_group_layout.addRow("Description:", self.description_label)
        
        self.priority_label = QLabel("-")
        details_group_layout.addRow("Priority:", self.priority_label)
        
        self.deadline_label = QLabel("-")
        details_group_layout.addRow("Deadline:", self.deadline_label)
        
        self.status_label = QLabel("-")
        details_group_layout.addRow("Status:", self.status_label)
        
        right_layout.addWidget(self.details_group)
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter)
    
    def add_task(self):
        dialog = TaskDialog(None, self)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            if task_data:
                task = Task(**task_data)
                self.tasks.append(task)
                self.save_tasks()
                self.update_task_list()
    
    def edit_task(self):
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.UserRole)
            dialog = TaskDialog(task, self)
            if dialog.exec_() == QDialog.Accepted:
                task_data = dialog.get_task_data()
                if task_data:
                    task.title = task_data['title']
                    task.description = task_data['description']
                    task.priority = task_data['priority']
                    task.deadline = task_data['deadline']
                    task.deadline_time = task_data['deadline_time']
                    task.notify_enabled = task_data['notify_enabled']
                    task.notify_before_minutes = task_data['notify_before_minutes']
                    self.save_tasks()
                    self.update_task_list()
                    # Find the updated item after the list is refreshed
                    for i in range(self.task_list.count()):
                        item = self.task_list.item(i)
                        if item and item.data(Qt.UserRole) == task:
                            self.task_list.setCurrentItem(item)
                            self.on_task_selected(item)
                            break
    
    def delete_task(self):
        current_item = self.task_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, 'Delete Task', 
                                       'Are you sure you want to delete this task?',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                task = current_item.data(Qt.UserRole)
                self.tasks.remove(task)
                self.save_tasks()
                self.update_task_list()
                self.clear_details()
    
    def toggle_task_completion(self):
        current_item = self.task_list.currentItem()
        if current_item:
            task = current_item.data(Qt.UserRole)
            task.completed = not task.completed
            self.save_tasks()
            self.update_task_list()
            # Find the updated item after the list is refreshed
            for i in range(self.task_list.count()):
                item = self.task_list.item(i)
                if item and item.data(Qt.UserRole) == task:
                    self.task_list.setCurrentItem(item)
                    self.on_task_selected(item)
                    break
    
    def on_task_selected(self, item):
        task = item.data(Qt.UserRole)
        self.details_group.setEnabled(True)
        
        self.title_label.setText(task.title)
        self.description_label.setText(task.description or "No description")
        
        # Priority with color coding
        priority_text = task.priority
        if task.priority == "High":
            self.priority_label.setText(f"🔴 {priority_text}")
        elif task.priority == "Medium":
            self.priority_label.setText(f"🟡 {priority_text}")
        else:
            self.priority_label.setText(f"🟢 {priority_text}")
        
        # Deadline with overdue check
        deadline_dt = task.get_deadline_datetime()
        if deadline_dt:
            if task.is_overdue():
                self.deadline_label.setText(f"⚠️ {deadline_dt.strftime('%Y-%m-%d %H:%M')} (OVERDUE)")
                self.deadline_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.deadline_label.setText(deadline_dt.strftime('%Y-%m-%d %H:%M'))
                self.deadline_label.setStyleSheet("")
        else:
            self.deadline_label.setText("No deadline")
            self.deadline_label.setStyleSheet("")
        
        # Status
        status_text = "✅ Completed" if task.completed else "⏳ Pending"
        self.status_label.setText(status_text)
        
        # Enable action buttons
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.toggle_button.setEnabled(True)
        self.toggle_button.setText("Mark Complete" if not task.completed else "Mark Incomplete")
    
    def clear_details(self):
        self.details_group.setEnabled(False)
        self.title_label.setText("-")
        self.description_label.setText("-")
        self.priority_label.setText("-")
        self.deadline_label.setText("-")
        self.status_label.setText("-")
        self.deadline_label.setStyleSheet("")
        
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
    
    def update_task_list(self):
        self.task_list.clear()
        filter_text = self.filter_combo.currentText()
        
        filtered_tasks = []
        
        for task in self.tasks:
            if filter_text == "All":
                filtered_tasks.append(task)
            elif filter_text == "High Priority" and task.priority == "High":
                filtered_tasks.append(task)
            elif filter_text == "Medium Priority" and task.priority == "Medium":
                filtered_tasks.append(task)
            elif filter_text == "Low Priority" and task.priority == "Low":
                filtered_tasks.append(task)
            elif filter_text == "Overdue" and task.is_overdue():
                filtered_tasks.append(task)
            elif filter_text == "Completed" and task.completed:
                filtered_tasks.append(task)
        
        # Sort tasks by priority and deadline
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        filtered_tasks.sort(key=lambda t: (
            -priority_order.get(t.priority, 2),  # Higher priority first
            t.get_deadline_datetime() or datetime.max,  # Tasks with deadlines first
            t.title.lower()
        ))
        
        for task in filtered_tasks:
            item = QListWidgetItem()
            
            # Create display text
            status_icon = "✅" if task.completed else "⏳"
            priority_icon = "🔴" if task.priority == "High" else "🟡" if task.priority == "Medium" else "🟢"
            
            display_text = f"{status_icon} {priority_icon} {task.title}"
            
            deadline_dt = task.get_deadline_datetime()
            if deadline_dt:
                if task.is_overdue():
                    display_text += f" ⚠️ OVERDUE ({deadline_dt.strftime('%m/%d %H:%M')})"
                else:
                    display_text += f" 📅 {deadline_dt.strftime('%m/%d %H:%M')}"
            
            # Add notification indicator
            if task.notify_enabled and not task.completed and not task.notified:
                display_text += " 🔔"
            
            item.setText(display_text)
            item.setData(Qt.UserRole, task)
            
            # Style based on completion and priority
            if task.completed:
                item.setBackground(QColor(240, 248, 255))  # Light blue
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            elif task.priority == "High":
                item.setBackground(QColor(255, 240, 240))  # Light red
            elif task.priority == "Medium":
                item.setBackground(QColor(255, 255, 240))  # Light yellow
            
            self.task_list.addItem(item)
    
    def check_overdue_and_notifications(self):
        # Check for overdue tasks
        overdue_count = sum(1 for task in self.tasks if task.is_overdue())
        
        if overdue_count > 0:
            self.setWindowTitle(f"To-Do List Manager - {overdue_count} Overdue Task(s)")
        else:
            self.setWindowTitle("To-Do List Manager")
        
        # Check for notifications
        for task in self.tasks:
            if task.should_notify():
                self.show_notification(task)
                task.notified = True
                self.save_tasks()
    
    def show_notification(self, task):
        """Show a notification dialog for a task"""
        deadline_dt = task.get_deadline_datetime()
        if deadline_dt:
            time_str = deadline_dt.strftime("%Y-%m-%d %H:%M")
            message = f"Task: {task.title}\nDeadline: {time_str}\nPriority: {task.priority}"
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Task Deadline Reminder")
            msg_box.setText("Deadline approaching!")
            msg_box.setInformativeText(message)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
    
    def save_tasks(self):
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save tasks: {str(e)}")
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tasks: {str(e)}")
            self.tasks = []


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = TodoApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
