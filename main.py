import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import sqlite3
import random


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def initialize_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Tasks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                assigned_to TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def execute_query(self, query, parameters=()):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        conn.commit()
        conn.close()

    def fetch_all(self, query, parameters=()):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        result = cursor.fetchall()
        conn.close()
        return result


class Employee:
    def __init__(self, name):
        self.name = name

    def insert_into_db(self, db_manager):
        db_manager.execute_query("INSERT INTO Employees (name) VALUES (?)", (self.name,))


class Task:
    def __init__(self, name):
        self.name = name

    def insert_into_db(self, db_manager):
        db_manager.execute_query("INSERT INTO Tasks (name) VALUES (?)", (self.name,))


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            parent=None,
            title="Сервис автоматического распределения задач для выездных сотрудников",
        )

        panel = self.populate()
        panel.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calibri"))

        self.db_manager = DatabaseManager("tasks.db")
        self.db_manager.initialize_db()

        self.resized = False  # the dirty flag
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.Show()
        self.Maximize(True)

    def OnSize(self, event):
        self.resized = True  # set dirty
        event.Skip()

    def OnIdle(self, event):
        if self.resized:
            # take action if the dirty flag is set
            print("New size:", self.GetSize())
            self.resized = False  # reset the flagass
            for i in range(3):
                self.list.SetColumnWidth(i, int(self.GetSize()[0] / 3))

    def populate(self):
        panel = wx.Panel(self)
        # остальной код без изменений

    def on_showTasksPress(self, event):
        self.list.DeleteAllItems()
        tasks = self.db_manager.fetch_all("SELECT * FROM Tasks")
        for task in tasks:
            self.list.Append(list(task))

    def on_giveTasksPress(self, event):
        task_ids = self.db_manager.fetch_all("SELECT id FROM Tasks WHERE assigned_to IS NULL")
        employee_ids = self.db_manager.fetch_all("SELECT id FROM Employees")
        if employee_ids:
            for task_id in task_ids:
                employee_id = random.choice(employee_ids)[0]
                self.db_manager.execute_query(
                    "UPDATE Tasks SET assigned_to = (SELECT name FROM Employees WHERE id = ?) WHERE id = ?",
                    (employee_id, task_id[0]),
                )
        else:
            wx.MessageBox(
                "Чтобы распределить задачи по сотрудникам, нужен хотя бы один сотрудник",
                "Не хватает сотрудников для распределения задач",
                wx.OK | wx.ICON_ERROR,
            )
        self.on_showTasksPress(event)

    def on_addEmployeeConfirmPress(self, event):
        name = self.name.GetValue()
        surname = self.surname.GetValue()
        middlename = self.middlename.GetValue() or ""
        if name and surname:
            fullname = " ".join([name.strip(), middlename.strip(), surname.strip()])
            employee = Employee(fullname)
            employee.insert_into_db(self.db_manager)
            for widget in [self.name, self.surname, self.middlename]:
                widget.SetValue("")
        else:
            wx.MessageBox(
                "Имя и фамилия являются обязательными полями",
                "Недопустимое имя",
                wx.OK | wx.ICON_ERROR,
            )

    def on_addTaskConfirmPress(self, event):
        taskname = self.taskName.GetValue()
        if taskname:
            task = Task(taskname)
            task.insert_into_db(self.db_manager)
            self.taskName.SetValue("")
        else:
            wx.MessageBox(
                "Название задачи не может быть пустым",
                "Недопустимое имя задачи",
                wx.OK | wx.ICON_ERROR,
            )


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
