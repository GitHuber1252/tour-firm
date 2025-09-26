import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

DB_FILE = 'database.json'

def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": [], "hotels": [], "rooms": []}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def register_window(root):
    win = tk.Toplevel(root)
    win.title("Регистрация")

    tk.Label(win, text="Логин:").grid(row=0, column=0)
    login_entry = tk.Entry(win)
    login_entry.grid(row=0, column=1)

    tk.Label(win, text="Пароль:").grid(row=1, column=0)
    pass_entry = tk.Entry(win, show='*')
    pass_entry.grid(row=1, column=1)

    tk.Label(win, text="Роль (admin/client):").grid(row=2, column=0)
    role_entry = tk.Entry(win)
    role_entry.grid(row=2, column=1)

    def do_register():
        data = load_data()
        data['users'].append({
            "login": login_entry.get(),
            "password": pass_entry.get(),
            "role": role_entry.get()
        })
        save_data(data)
        messagebox.showinfo("Успех", "Регистрация успешна!")
        win.destroy()

    tk.Button(win, text="Регистрация", command=do_register).grid(row=3, column=0, columnspan=2)

def login_window(root):
    win = tk.Toplevel(root)
    win.title("Вход")

    tk.Label(win, text="Логин:").grid(row=0, column=0)
    login_entry = tk.Entry(win)
    login_entry.grid(row=0, column=1)

    tk.Label(win, text="Пароль:").grid(row=1, column=0)
    pass_entry = tk.Entry(win, show='*')
    pass_entry.grid(row=1, column=1)

    def do_login():
        data = load_data()
        login = login_entry.get()
        password = pass_entry.get()
        for user in data['users']:
            if user['login'] == login and user['password'] == password:
                messagebox.showinfo("Успех", f"Добро пожаловать, {user['role']}!")
                win.destroy()
                if user['role'] == 'admin':
                    admin_window(root)
                else:
                    client_window(root)
                return
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

    tk.Button(win, text="Войти", command=do_login).grid(row=2, column=0, columnspan=2)

def admin_window(root):
    win = tk.Toplevel(root)
    win.title("Администратор")

    def add_hotel():
        name = simpledialog.askstring("Гостиница", "Введите название гостиницы:")
        if name:
            data = load_data()
            data['hotels'].append({"name": name})
            save_data(data)
            messagebox.showinfo("Успех", "Гостиница добавлена")

    def add_room():
        hotel = simpledialog.askstring("Номер", "Название гостиницы:")
        room_id = simpledialog.askstring("Номер", "ID номера:")
        if hotel and room_id:
            data = load_data()
            data['rooms'].append({"hotel": hotel, "room_id": room_id, "status": "available"})
            save_data(data)
            messagebox.showinfo("Успех", "Номер добавлен")

    def show_hotels():
        data = load_data()
        hotels = "\n".join([h['name'] for h in data['hotels']])
        messagebox.showinfo("Гостиницы", hotels if hotels else "Нет гостиниц")

    tk.Button(win, text="Добавить гостиницу", command=add_hotel).pack(fill='x')
    tk.Button(win, text="Добавить номер", command=add_room).pack(fill='x')
    tk.Button(win, text="Посмотреть гостиницы", command=show_hotels).pack(fill='x')


def client_window(root):
    win = tk.Toplevel(root)
    win.title("Клиент")

    def view_rooms():
        data = load_data()
        available = [r for r in data['rooms'] if r['status'] == 'available']
        text = "\n".join([f"{r['hotel']} - {r['room_id']}" for r in available])
        messagebox.showinfo("Доступные номера", text if text else "Нет доступных номеров")

    def book_room():
        room_id = simpledialog.askstring("Бронирование", "Введите ID номера:")
        data = load_data()
        for r in data['rooms']:
            if r['room_id'] == room_id and r['status'] == 'available':
                r['status'] = 'booked'
                save_data(data)
                messagebox.showinfo("Успех", "Номер забронирован")
                return
        messagebox.showerror("Ошибка", "Нет доступного номера")

    tk.Button(win, text="Посмотреть доступные номера", command=view_rooms).pack(fill='x')
    tk.Button(win, text="Забронировать номер", command=book_room).pack(fill='x')


def main():
    root = tk.Tk()
    root.title("Турфирма")

    tk.Button(root, text="Регистрация", command=lambda: register_window(root)).pack(fill='x')
    tk.Button(root, text="Вход", command=lambda: login_window(root)).pack(fill='x')

    root.mainloop()

if __name__ == "__main__":
    main()
