import json
import os
import tkinter as tk
<<<<<<< HEAD
from tkinter import messagebox, simpledialog, ttk

DB_FILE = 'database.json'


def load_data():
    default_data = {"users": [], "hotels": [], "rooms": []}

    # если файл не существует — создаём
    if not os.path.exists(DB_FILE):
        save_data(default_data)
        return default_data

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # если файл повреждён или пуст
        save_data(default_data)
        return default_data

    # проверка на наличие всех ключей
    for key in default_data:
        if key not in data:
            data[key] = []

    return data


=======
from tkinter import messagebox, simpledialog

DB_FILE = 'database.json'

def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": [], "hotels": [], "rooms": []}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)
>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

<<<<<<< HEAD

# ------------------- РЕГИСТРАЦИЯ -------------------
def register_window(root):
    win = tk.Toplevel(root)
    win.title("Регистрация")
    win.geometry("500x250")
=======
def register_window(root):
    win = tk.Toplevel(root)
    win.title("Регистрация")
>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6

    tk.Label(win, text="Логин:").grid(row=0, column=0)
    login_entry = tk.Entry(win)
    login_entry.grid(row=0, column=1)

    tk.Label(win, text="Пароль:").grid(row=1, column=0)
    pass_entry = tk.Entry(win, show='*')
    pass_entry.grid(row=1, column=1)

<<<<<<< HEAD
    tk.Label(win, text="Роль (admin/client/hotel):").grid(row=2, column=0)
=======
    tk.Label(win, text="Роль (admin/client):").grid(row=2, column=0)
>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6
    role_entry = tk.Entry(win)
    role_entry.grid(row=2, column=1)

    def do_register():
        data = load_data()
<<<<<<< HEAD
        login = login_entry.get()
        password = pass_entry.get()
        role = role_entry.get()

        if not all([login, password, role]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        # Проверка уникальности логина
        if any(u['login'] == login for u in data['users']):
            messagebox.showerror("Ошибка", "Такой логин уже существует!")
            return

        user_data = {"login": login, "password": password, "role": role}

        # Если это регистрация гостиницы
        if role == "hotel":
            hotel_name = simpledialog.askstring("Регистрация гостиницы", "Введите название гостиницы:")
            hotel_id = str(len(data["hotels"]) + 1)
            user_data["hotel_id"] = hotel_id
            user_data["hotel_name"] = hotel_name
            data["hotels"].append({"id": hotel_id, "name": hotel_name, "rooms": []})
            messagebox.showinfo("Информация", f"ID вашей гостиницы: {hotel_id}")

        data['users'].append(user_data)
=======
        data['users'].append({
            "login": login_entry.get(),
            "password": pass_entry.get(),
            "role": role_entry.get()
        })
>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6
        save_data(data)
        messagebox.showinfo("Успех", "Регистрация успешна!")
        win.destroy()

    tk.Button(win, text="Регистрация", command=do_register).grid(row=3, column=0, columnspan=2)

<<<<<<< HEAD

# ------------------- ВХОД -------------------
def login_window(root):
    win = tk.Toplevel(root)
    win.title("Вход")
    win.geometry("500x250")
=======
def login_window(root):
    win = tk.Toplevel(root)
    win.title("Вход")
>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6

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
<<<<<<< HEAD
                elif user['role'] == 'hotel':
                    hotel_window(root, user)
                else:
                    client_window(root, user)
=======
                else:
                    client_window(root)
>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6
                return
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

    tk.Button(win, text="Войти", command=do_login).grid(row=2, column=0, columnspan=2)

<<<<<<< HEAD

# ------------------- АДМИН -------------------
def admin_window(root):
    win = tk.Toplevel(root)
    win.title("Администратор")
    win.geometry("600x400")

    def show_hotels():
        data = load_data()

        hotels_win = tk.Toplevel(win)
        hotels_win.title("Все гостиницы")
        hotels_win.geometry("600x400")

        tree = ttk.Treeview(hotels_win, columns=("ID", "Name"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Название гостиницы")
        tree.pack(fill='both', expand=True)

        for h in data['hotels']:
            tree.insert('', 'end', values=(h['id'], h['name']))

        def delete_hotel():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Ошибка", "Выберите гостиницу для удаления!")
                return
            hotel_id = tree.item(selected[0])['values'][0]
            data['hotels'] = [h for h in data['hotels'] if h['id'] != str(hotel_id)]
            data['rooms'] = [r for r in data['rooms'] if r['hotel_id'] != str(hotel_id)]
            save_data(data)
            tree.delete(selected[0])
            messagebox.showinfo("Успех", "Гостиница удалена!")

        def edit_hotel():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Ошибка", "Выберите гостиницу для редактирования!")
                return
            hotel_id = tree.item(selected[0])['values'][0]
            new_name = simpledialog.askstring("Редактирование", "Введите новое название гостиницы:")
            for h in data['hotels']:
                if h['id'] == str(hotel_id):
                    h['name'] = new_name
            save_data(data)
            tree.item(selected[0], values=(hotel_id, new_name))
            messagebox.showinfo("Успех", "Название гостиницы обновлено!")

        tk.Button(hotels_win, text="Удалить гостиницу", command=delete_hotel).pack(fill='x')
        tk.Button(hotels_win, text="Редактировать гостиницу", command=edit_hotel).pack(fill='x')

    tk.Button(win, text="Посмотреть все гостиницы", command=show_hotels).pack(fill='x')


# ------------------- ГОСТИНИЦА -------------------
def hotel_window(root, hotel_user):
    win = tk.Toplevel(root)
    win.title(f"Гостиница {hotel_user['hotel_name']}")
    win.geometry("700x400")

    tree = ttk.Treeview(win, columns=("RoomID", "Status", "BookedBy"), show="headings")
    tree.heading("RoomID", text="ID Номера")
    tree.heading("Status", text="Статус")
    tree.heading("BookedBy", text="Забронирован кем")
    tree.pack(fill='both', expand=True)

    def refresh_rooms():
        tree.delete(*tree.get_children())
        data = load_data()
        rooms = [r for r in data['rooms'] if r['hotel_id'] == hotel_user['hotel_id']]
        for r in rooms:
            tree.insert('', 'end', values=(r['room_id'], r['status'], r['booked_by'] or ""))

    def add_room():
        room_id = simpledialog.askstring("Добавление номера", "Введите ID номера:")
        if not room_id:
            return
        data = load_data()
        for hotel in data['hotels']:
            if hotel['id'] == hotel_user['hotel_id']:
                hotel['rooms'].append({"room_id": room_id, "status": "available", "booked_by": None})
                data['rooms'].append({
                    "hotel": hotel_user['hotel_name'],
                    "hotel_id": hotel_user['hotel_id'],
                    "room_id": room_id,
                    "status": "available",
                    "booked_by": None
                })
                save_data(data)
                refresh_rooms()
                return

    def delete_room():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для удаления!")
            return
        room_id = tree.item(selected[0])['values'][0]
        data = load_data()
        for hotel in data['hotels']:
            if hotel['id'] == hotel_user['hotel_id']:
                hotel['rooms'] = [r for r in hotel['rooms'] if r['room_id'] != room_id]
        data['rooms'] = [r for r in data['rooms'] if not (r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id)]
        save_data(data)
        refresh_rooms()

    def edit_room():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для редактирования!")
            return
        room_id = tree.item(selected[0])['values'][0]
        new_status = simpledialog.askstring("Редактирование", "Введите новый статус (available/booked):")
        if new_status not in ("available", "booked"):
            messagebox.showerror("Ошибка", "Недопустимый статус.")
            return
        data = load_data()
        for r in data['rooms']:
            if r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id:
                r['status'] = new_status
                r['booked_by'] = None if new_status == "available" else r['booked_by']
        save_data(data)
        refresh_rooms()

    tk.Button(win, text="Добавить номер", command=add_room).pack(fill='x')
    tk.Button(win, text="Удалить номер", command=delete_room).pack(fill='x')
    tk.Button(win, text="Редактировать номер", command=edit_room).pack(fill='x')
    refresh_rooms()


# ------------------- КЛИЕНТ -------------------
def client_window(root, client_user):
    win = tk.Toplevel(root)
    win.title("Клиент")
    win.geometry("700x400")

    tk.Label(win, text="Фильтр:").pack()
    filter_var = tk.StringVar(value="available")
    ttk.Combobox(win, textvariable=filter_var, values=["available", "booked", "all"]).pack()

    tree = ttk.Treeview(win, columns=("Hotel", "RoomID", "Status"), show="headings")
    tree.heading("Hotel", text="Гостиница")
    tree.heading("RoomID", text="ID Номера")
    tree.heading("Status", text="Статус")
    tree.pack(fill='both', expand=True)

    def refresh_rooms():
        tree.delete(*tree.get_children())
        data = load_data()
        rooms = data['rooms']
        filt = filter_var.get()
        if filt != "all":
            rooms = [r for r in rooms if r['status'] == filt]
        for r in rooms:
            tree.insert('', 'end', values=(r['hotel'], r['room_id'], r['status']))

    def book_room():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для бронирования!")
            return
        hotel_name, room_id, status = tree.item(selected[0])['values']
        if status != "available":
            messagebox.showerror("Ошибка", "Номер уже забронирован!")
            return
        data = load_data()
        for r in data['rooms']:
            if r['hotel'] == hotel_name and r['room_id'] == room_id:
                r['status'] = 'booked'
                r['booked_by'] = client_user['login']
        save_data(data)
        refresh_rooms()
        messagebox.showinfo("Успех", f"Номер {room_id} в гостинице {hotel_name} забронирован")

    tk.Button(win, text="Обновить", command=refresh_rooms).pack(fill='x')
    tk.Button(win, text="Забронировать выбранный номер", command=book_room).pack(fill='x')
    refresh_rooms()


# ------------------- ГЛАВНОЕ ОКНО -------------------
def main():
    root = tk.Tk()
    root.title("Система бронирования турфирмы")
    root.geometry("500x250")

    tk.Button(root, text="Регистрация", command=lambda: register_window(root)).pack(fill='x', pady=10)
    tk.Button(root, text="Вход", command=lambda: login_window(root)).pack(fill='x', pady=10)

    root.mainloop()


=======
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

>>>>>>> 0ed7fddc3f232383a9902c3e0d0f2f393c8b9de6
if __name__ == "__main__":
    main()
