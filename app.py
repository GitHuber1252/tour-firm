import json
import os, sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
DB_FILE = DB_FILE = os.path.join(BASE_DIR, 'database.json')

def load_data():
    default_data = {"users": [], "hotels": [], "rooms": []}

    if not os.path.exists(DB_FILE):
        save_data(default_data)
        return default_data

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        save_data(default_data)
        return default_data

    for key in default_data:
        if key not in data:
            data[key] = []

    return data

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def center_window(window):
    """Центрирует окно на экране"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# ------------------- РЕГИСТРАЦИЯ -------------------
def register_window(root):
    win = tk.Toplevel(root)
    win.title("Регистрация")
    win.geometry("400x250")
    win.transient(root)
    win.grab_set()

    tk.Label(win, text="Логин:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    login_entry = tk.Entry(win, width=20)
    login_entry.grid(row=0, column=1, padx=10, pady=10)
    login_entry.focus()

    tk.Label(win, text="Пароль:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    pass_entry = tk.Entry(win, show='*', width=20)
    pass_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(win, text="Роль (admin/client/hotel):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    role_entry = ttk.Combobox(win, values=["admin", "client", "hotel"], width=17)
    role_entry.grid(row=2, column=1, padx=10, pady=10)

    def do_register():
        data = load_data()
        login = login_entry.get().strip()
        password = pass_entry.get().strip()
        role = role_entry.get().strip()

        if not all([login, password, role]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if role not in ["admin", "client", "hotel"]:
            messagebox.showerror("Ошибка", "Роль должна быть: admin, client или hotel!")
            return

        if any(u['login'] == login for u in data['users']):
            messagebox.showerror("Ошибка", "Такой логин уже существует!")
            return

        user_data = {"login": login, "password": password, "role": role}

        if role == "hotel":
            hotel_name = simpledialog.askstring("Регистрация гостиницы", "Введите название гостиницы:")
            if not hotel_name:
                messagebox.showerror("Ошибка", "Название гостиницы обязательно!")
                return
            hotel_id = str(len(data["hotels"]) + 1)
            user_data["hotel_id"] = hotel_id
            user_data["hotel_name"] = hotel_name
            data["hotels"].append({"id": hotel_id, "name": hotel_name, "rooms": []})
            messagebox.showinfo("Информация", f"ID вашей гостиницы: {hotel_id}")

        data['users'].append(user_data)
        save_data(data)
        messagebox.showinfo("Успех", "Регистрация успешна!")
        
        if messagebox.askyesno("Успех", "Регистрация завершена! Хотите войти сейчас?"):
            win.destroy()
            login_window(root)
        else:
            win.destroy()

    button_frame = tk.Frame(win)
    button_frame.grid(row=4, column=0, columnspan=2, pady=20)

    tk.Button(button_frame, text="Регистрация", command=do_register, width=15).pack(side='left', padx=5)
    tk.Button(button_frame, text="Войти", command=lambda: [win.destroy(), login_window(root)], width=15).pack(side='left', padx=5)

    center_window(win)

# ------------------- ВХОД -------------------
def login_window(root):
    win = tk.Toplevel(root)
    win.title("Вход")
    win.geometry("400x200")
    win.transient(root)
    win.grab_set()

    tk.Label(win, text="Логин:").grid(row=0, column=0, padx=10, pady=15, sticky='e')
    login_entry = tk.Entry(win, width=20)
    login_entry.grid(row=0, column=1, padx=10, pady=15)
    login_entry.focus()

    tk.Label(win, text="Пароль:").grid(row=1, column=0, padx=10, pady=15, sticky='e')
    pass_entry = tk.Entry(win, show='*', width=20)
    pass_entry.grid(row=1, column=1, padx=10, pady=15)

    def do_login():
        data = load_data()
        login = login_entry.get().strip()
        password = pass_entry.get().strip()
        
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            return
            
        for user in data['users']:
            if user['login'] == login and user['password'] == password:
                messagebox.showinfo("Успех", f"Добро пожаловать, {user['role']}!")
                win.destroy()
                if user['role'] == 'admin':
                    admin_window(root)
                elif user['role'] == 'hotel':
                    hotel_window(root, user)
                else:
                    client_window(root, user)
                return
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def on_enter(event):
        do_login()

    login_entry.bind('<Return>', on_enter)
    pass_entry.bind('<Return>', on_enter)

    button_frame = tk.Frame(win)
    button_frame.grid(row=3, column=0, columnspan=2, pady=20)

    tk.Button(button_frame, text="Войти", command=do_login, width=15).pack(side='left', padx=5)
    tk.Button(button_frame, text="Регистрация", command=lambda: [win.destroy(), register_window(root)], width=15).pack(side='left', padx=5)

    center_window(win)

# ------------------- ФУНКЦИИ АДМИНИСТРАТОРА -------------------
def show_hotels_admin(win):
    data = load_data()

    hotels_win = tk.Toplevel(win)
    hotels_win.title("Управление гостиницами")
    hotels_win.geometry("800x500")

    tree = ttk.Treeview(hotels_win, columns=("ID", "Name", "Rooms", "Owner"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Название гостиницы")
    tree.heading("Rooms", text="Количество номеров")
    tree.heading("Owner", text="Владелец")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    # Заполняем таблицу
    for h in data['hotels']:
        room_count = len([r for r in data['rooms'] if r['hotel_id'] == h['id']])
        # Находим владельца гостиницы
        owner = "Не назначен"
        for user in data['users']:
            if user.get('hotel_id') == h['id']:
                owner = user['login']
                break
        tree.insert('', 'end', values=(h['id'], h['name'], room_count, owner))

    control_frame = tk.Frame(hotels_win)
    control_frame.pack(fill='x', padx=10, pady=10)

    tk.Button(control_frame, text="Обновить", command=lambda: [hotels_win.destroy(), show_hotels_admin(win)]).pack(side='left', padx=5)

    center_window(hotels_win)

def add_hotel_admin(win):
    hotel_name = simpledialog.askstring("Добавление гостиницы", "Введите название гостиницы:")
    if not hotel_name:
        return

    data = load_data()
    hotel_id = str(len(data["hotels"]) + 1)
    
    # Создаем гостиницу
    data["hotels"].append({"id": hotel_id, "name": hotel_name, "rooms": []})
    
    # Создаем пользователя для гостиницы
    hotel_login = f"hotel_{hotel_id}"
    hotel_password = "password123"  # Можно сделать генерацию случайного пароля
    
    data['users'].append({
        "login": hotel_login,
        "password": hotel_password,
        "role": "hotel",
        "hotel_id": hotel_id,
        "hotel_name": hotel_name
    })
    
    save_data(data)
    messagebox.showinfo("Успех", f"Гостиница '{hotel_name}' добавлена!\nID: {hotel_id}\nЛогин: {hotel_login}\nПароль: {hotel_password}")

def delete_hotel_admin(win):
    data = load_data()
    
    if not data['hotels']:
        messagebox.showinfo("Информация", "Нет гостиниц для удаления")
        return
        
    delete_win = tk.Toplevel(win)
    delete_win.title("Удаление гостиницы")
    delete_win.geometry("600x400")
    
    tree = ttk.Treeview(delete_win, columns=("ID", "Name", "Rooms"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Название гостиницы")
    tree.heading("Rooms", text="Количество номеров")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for h in data['hotels']:
        room_count = len([r for r in data['rooms'] if r['hotel_id'] == h['id']])
        tree.insert('', 'end', values=(h['id'], h['name'], room_count))

    def do_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите гостиницу для удаления!")
            return
            
        hotel_id = tree.item(selected[0])['values'][0]
        hotel_name = tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите удалить гостиницу '{hotel_name}'?\nЭто действие удалит все номера и пользователя гостиницы."):
            data['hotels'] = [h for h in data['hotels'] if h['id'] != str(hotel_id)]
            data['rooms'] = [r for r in data['rooms'] if r['hotel_id'] != str(hotel_id)]
            data['users'] = [u for u in data['users'] if u.get('hotel_id') != str(hotel_id)]
            save_data(data)
            messagebox.showinfo("Успех", "Гостиница удалена!")
            delete_win.destroy()

    tk.Button(delete_win, text="Удалить выбранную гостиницу", command=do_delete, bg='red', fg='white').pack(pady=10)
    center_window(delete_win)

def show_all_rooms_admin(win):
    data = load_data()

    rooms_win = tk.Toplevel(win)
    rooms_win.title("Все номера")
    rooms_win.geometry("900x500")

    tree = ttk.Treeview(rooms_win, columns=("Hotel", "RoomID", "Status", "BookedBy"), show="headings")
    tree.heading("Hotel", text="Гостиница")
    tree.heading("RoomID", text="ID Номера")
    tree.heading("Status", text="Статус")
    tree.heading("BookedBy", text="Забронирован кем")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for r in data['rooms']:
        status_text = "Свободен" if r['status'] == "available" else "Забронирован"
        booked_by = r.get('booked_by', '') or ""
        tree.insert('', 'end', values=(r['hotel'], r['room_id'], status_text, booked_by))

    center_window(rooms_win)

def add_room_admin(win):
    data = load_data()
    
    if not data['hotels']:
        messagebox.showerror("Ошибка", "Нет гостиниц! Сначала добавьте гостиницу.")
        return
        
    add_win = tk.Toplevel(win)
    add_win.title("Добавление номера")
    add_win.geometry("400x200")
    
    tk.Label(add_win, text="Выберите гостиницу:").pack(pady=10)
    
    hotel_var = tk.StringVar()
    hotel_combo = ttk.Combobox(add_win, textvariable=hotel_var, 
                              values=[h['name'] for h in data['hotels']], width=30)
    hotel_combo.pack(pady=5)
    
    tk.Label(add_win, text="ID номера:").pack(pady=10)
    room_id_entry = tk.Entry(add_win, width=30)
    room_id_entry.pack(pady=5)

    def do_add():
        hotel_name = hotel_var.get()
        room_id = room_id_entry.get().strip()
        
        if not hotel_name or not room_id:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
            
        # Находим ID гостиницы
        hotel_id = None
        for h in data['hotels']:
            if h['name'] == hotel_name:
                hotel_id = h['id']
                break
                
        if not hotel_id:
            messagebox.showerror("Ошибка", "Гостиница не найдена!")
            return
            
        # Проверяем, существует ли номер
        existing_room = next((r for r in data['rooms'] if r['hotel_id'] == hotel_id and r['room_id'] == room_id), None)
        if existing_room:
            messagebox.showerror("Ошибка", "Номер с таким ID уже существует в этой гостинице!")
            return
            
        # Добавляем номер
        data['rooms'].append({
            "hotel": hotel_name,
            "hotel_id": hotel_id,
            "room_id": room_id,
            "status": "available",
            "booked_by": None
        })
        
        save_data(data)
        messagebox.showinfo("Успех", f"Номер {room_id} добавлен в гостиницу {hotel_name}!")
        add_win.destroy()

    tk.Button(add_win, text="Добавить номер", command=do_add, bg='green', fg='white').pack(pady=10)
    center_window(add_win)

def delete_room_admin(win):
    data = load_data()
    
    delete_win = tk.Toplevel(win)
    delete_win.title("Удаление номера")
    delete_win.geometry("800x500")
    
    tree = ttk.Treeview(delete_win, columns=("Hotel", "RoomID", "Status", "BookedBy"), show="headings")
    tree.heading("Hotel", text="Гостиница")
    tree.heading("RoomID", text="ID Номера")
    tree.heading("Status", text="Статус")
    tree.heading("BookedBy", text="Забронирован кем")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for r in data['rooms']:
        status_text = "Свободен" if r['status'] == "available" else "Забронирован"
        booked_by = r.get('booked_by', '') or ""
        tree.insert('', 'end', values=(r['hotel'], r['room_id'], status_text, booked_by))

    def do_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для удаления!")
            return
            
        hotel_name, room_id, status, booked_by = tree.item(selected[0])['values']
        
        if messagebox.askyesno("Подтверждение", f"Удалить номер {room_id} из гостиницы {hotel_name}?"):
            data['rooms'] = [r for r in data['rooms'] if not (r['hotel'] == hotel_name and r['room_id'] == room_id)]
            save_data(data)
            messagebox.showinfo("Успех", "Номер удален!")
            delete_win.destroy()

    tk.Button(delete_win, text="Удалить выбранный номер", command=do_delete, bg='red', fg='white').pack(pady=10)
    center_window(delete_win)

def show_clients_admin(win):
    data = load_data()
    
    clients_win = tk.Toplevel(win)
    clients_win.title("Список клиентов")
    clients_win.geometry("600x400")
    
    tree = ttk.Treeview(clients_win, columns=("Login", "Bookings"), show="headings")
    tree.heading("Login", text="Логин клиента")
    tree.heading("Bookings", text="Количество бронирований")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    clients = [u for u in data['users'] if u['role'] == 'client']
    for client in clients:
        booking_count = len([r for r in data['rooms'] if r.get('booked_by') == client['login']])
        tree.insert('', 'end', values=(client['login'], booking_count))

    center_window(clients_win)

def show_all_users_admin(win):
    data = load_data()
    
    users_win = tk.Toplevel(win)
    users_win.title("Все пользователи")
    users_win.geometry("700x400")
    
    tree = ttk.Treeview(users_win, columns=("Login", "Role", "Hotel"), show="headings")
    tree.heading("Login", text="Логин")
    tree.heading("Role", text="Роль")
    tree.heading("Hotel", text="Гостиница")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for user in data['users']:
        hotel_name = user.get('hotel_name', '') if user['role'] == 'hotel' else ''
        tree.insert('', 'end', values=(user['login'], user['role'], hotel_name))

    center_window(users_win)

def delete_user_admin(win):
    data = load_data()
    
    delete_win = tk.Toplevel(win)
    delete_win.title("Удаление пользователя")
    delete_win.geometry("700x400")
    
    tree = ttk.Treeview(delete_win, columns=("Login", "Role", "Hotel"), show="headings")
    tree.heading("Login", text="Логин")
    tree.heading("Role", text="Роль")
    tree.heading("Hotel", text="Гостиница")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for user in data['users']:
        if user['login'] != 'admin':  # Не показываем самого админа для удаления
            hotel_name = user.get('hotel_name', '') if user['role'] == 'hotel' else ''
            tree.insert('', 'end', values=(user['login'], user['role'], hotel_name))

    def do_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления!")
            return
            
        login, role, hotel = tree.item(selected[0])['values']
        
        if role == 'hotel':
            if messagebox.askyesno("Предупреждение", 
                                  f"Удаление пользователя гостиницы также удалит гостиницу '{hotel}' и все её номера. Продолжить?"):
                # Удаляем гостиницу и связанные данные
                hotel_id = next((u.get('hotel_id') for u in data['users'] if u['login'] == login), None)
                if hotel_id:
                    data['hotels'] = [h for h in data['hotels'] if h['id'] != hotel_id]
                    data['rooms'] = [r for r in data['rooms'] if r['hotel_id'] != hotel_id]
        elif role == 'client':
            # Освобождаем забронированные номера
            for room in data['rooms']:
                if room.get('booked_by') == login:
                    room['status'] = 'available'
                    room['booked_by'] = None
        
        data['users'] = [u for u in data['users'] if u['login'] != login]
        save_data(data)
        messagebox.showinfo("Успех", f"Пользователь {login} удален!")
        delete_win.destroy()

    tk.Button(delete_win, text="Удалить выбранного пользователя", command=do_delete, bg='red', fg='white').pack(pady=10)
    center_window(delete_win)

# ------------------- АДМИН -------------------
def admin_window(root):
    win = tk.Toplevel(root)
    win.title("Панель администратора")
    win.geometry("700x500")
    win.transient(root)
    win.grab_set()

    header_frame = tk.Frame(win)
    header_frame.pack(pady=20)

    tk.Label(header_frame, text="Панель администратора", font=('Arial', 16, 'bold')).pack()

    # Основные кнопки управления
    main_frame = tk.Frame(win)
    main_frame.pack(pady=20)

    # Управление гостиницами
    hotel_frame = tk.LabelFrame(main_frame, text="Управление гостиницами", padx=10, pady=10)
    hotel_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    tk.Button(hotel_frame, text="Просмотр списка гостиниц", command=lambda: show_hotels_admin(win), width=20, height=2).pack(pady=5)
    tk.Button(hotel_frame, text="Добавить гостиницу", command=lambda: add_hotel_admin(win), width=20, height=2).pack(pady=5)
    tk.Button(hotel_frame, text="Удалить гостиницу", command=lambda: delete_hotel_admin(win), width=20, height=2).pack(pady=5)

    # Управление номерами
    room_frame = tk.LabelFrame(main_frame, text="Управление номерами", padx=10, pady=10)
    room_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

    tk.Button(room_frame, text="Просмотр всех номеров", command=lambda: show_all_rooms_admin(win), width=20, height=2).pack(pady=5)
    tk.Button(room_frame, text="Добавить номер", command=lambda: add_room_admin(win), width=20, height=2).pack(pady=5)
    tk.Button(room_frame, text="Удалить номер", command=lambda: delete_room_admin(win), width=20, height=2).pack(pady=5)

    # Управление пользователями
    user_frame = tk.LabelFrame(main_frame, text="Управление пользователями", padx=10, pady=10)
    user_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

    tk.Button(user_frame, text="Просмотр списка клиентов", command=lambda: show_clients_admin(win), width=20, height=2).pack(side='left', padx=5)
    tk.Button(user_frame, text="Просмотр всех пользователей", command=lambda: show_all_users_admin(win), width=20, height=2).pack(side='left', padx=5)
    tk.Button(user_frame, text="Удалить пользователя", command=lambda: delete_user_admin(win), width=20, height=2).pack(side='left', padx=5)

    center_window(win)

# ------------------- ГОСТИНИЦА -------------------
def hotel_window(root, hotel_user):
    win = tk.Toplevel(root)
    win.title(f"Управление гостиницей: {hotel_user.get('hotel_name', '')}")
    win.geometry("800x500")
    win.transient(root)
    win.grab_set()

    header_frame = tk.Frame(win)
    header_frame.pack(pady=10)

    tk.Label(header_frame, text=f"Гостиница: {hotel_user.get('hotel_name', '')}", font=('Arial', 14, 'bold')).pack()
    tk.Label(header_frame, text=f"ID: {hotel_user.get('hotel_id', '')}").pack()

    tree = ttk.Treeview(win, columns=("RoomID", "Status", "BookedBy"), show="headings")
    tree.heading("RoomID", text="ID Номера")
    tree.heading("Status", text="Статус")
    tree.heading("BookedBy", text="Забронирован кем")
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_rooms():
        tree.delete(*tree.get_children())
        data = load_data()
        rooms = [r for r in data['rooms'] if r['hotel_id'] == hotel_user['hotel_id']]
        for r in rooms:
            status_text = "Свободен" if r['status'] == "available" else "Забронирован"
            booked_by = r.get('booked_by', '') or ""
            tree.insert('', 'end', values=(r['room_id'], status_text, booked_by))

    def add_room():
        room_id = simpledialog.askstring("Добавление номера", "Введите ID номера:")
        if not room_id:
            return
            
        room_id = room_id.strip()
        if not room_id:
            messagebox.showerror("Ошибка", "ID номера не может быть пустым!")
            return
            
        data = load_data()
        
        existing_room = next((r for r in data['rooms'] if r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id), None)
        if existing_room:
            messagebox.showerror("Ошибка", "Номер с таким ID уже существует!")
            return
            
        data['rooms'].append({
            "hotel": hotel_user['hotel_name'],
            "hotel_id": hotel_user['hotel_id'],
            "room_id": room_id,
            "status": "available",
            "booked_by": None
        })
        
        for hotel in data['hotels']:
            if hotel['id'] == hotel_user['hotel_id']:
                hotel['rooms'].append({"room_id": room_id, "status": "available", "booked_by": None})
                
        save_data(data)
        refresh_rooms()
        messagebox.showinfo("Успех", "Номер добавлен!")

    def delete_room():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для удаления!")
            return
        room_id = tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить номер {room_id}?"):
            data = load_data()
            data['rooms'] = [r for r in data['rooms'] if not (r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id)]
            for hotel in data['hotels']:
                if hotel['id'] == hotel_user['hotel_id']:
                    hotel['rooms'] = [r for r in hotel['rooms'] if r['room_id'] != room_id]
            save_data(data)
            refresh_rooms()
            messagebox.showinfo("Успех", "Номер удален!")

    def edit_room_status():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для изменения статуса!")
            return
            
        room_id = tree.item(selected[0])['values'][0]
        current_status = tree.item(selected[0])['values'][1]
        
        new_status = "available" if current_status == "Забронирован" else "booked"
        
        data = load_data()
        for r in data['rooms']:
            if r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id:
                r['status'] = new_status
                if new_status == "available":
                    r['booked_by'] = None
                    
        save_data(data)
        refresh_rooms()
        messagebox.showinfo("Успех", "Статус номера обновлен!")

    control_frame = tk.Frame(win)
    control_frame.pack(fill='x', padx=10, pady=10)

    tk.Button(control_frame, text="Добавить номер", command=add_room).pack(side='left', padx=5)
    tk.Button(control_frame, text="Удалить номер", command=delete_room).pack(side='left', padx=5)
    tk.Button(control_frame, text="Изменить статус", command=edit_room_status).pack(side='left', padx=5)
    tk.Button(control_frame, text="Обновить", command=refresh_rooms).pack(side='left', padx=5)
    
    refresh_rooms()
    center_window(win)

# ------------------- КЛИЕНТ -------------------
# ------------------- КЛИЕНТ -------------------
def client_window(root, client_user):
    win = tk.Toplevel(root)
    win.title("Бронирование номеров")
    win.geometry("1200x700")
    win.transient(root)
    win.grab_set()

    # ВНУТРЕННИЕ ФУНКЦИИ - объявляем ПЕРВЫМИ
    def load_hotels_list():
        """Загружает список гостиниц для фильтра"""
        data = load_data()
        hotels = list(set([r['hotel'] for r in data['rooms']]))
        hotels.sort()
        hotels.insert(0, "Все гостиницы")
        hotel_combo['values'] = hotels

    def reset_filters():
        """Сбрасывает все фильтры"""
        hotel_var.set("Все гостиницы")
        status_var.set("Свободен")
        room_id_var.set("")
        refresh_rooms()
        messagebox.showinfo("Фильтры", "Все фильтры сброшены!")

    def apply_filters(rooms):
        """Применяет фильтры к списку номеров"""
        filtered_rooms = rooms.copy()
        
        # Фильтр по гостинице
        hotel_filter = hotel_var.get()
        if hotel_filter != "Все гостиницы":
            filtered_rooms = [r for r in filtered_rooms if r['hotel'] == hotel_filter]
        
        # Фильтр по статусу
        status_filter = status_var.get()
        if status_filter == "Свободен":
            filtered_rooms = [r for r in filtered_rooms if r['status'] == "available"]
        elif status_filter == "Забронирован":
            filtered_rooms = [r for r in filtered_rooms if r['status'] == "booked"]
        # "Все" - без фильтрации
        
        # Фильтр по ID номера
        room_id_filter = room_id_var.get().strip()
        if room_id_filter:
            filtered_rooms = [r for r in filtered_rooms if room_id_filter.lower() in r['room_id'].lower()]
        
        return filtered_rooms

    def refresh_rooms():
        """Обновляет список номеров"""
        # Очищаем таблицу
        for item in tree.get_children():
            tree.delete(item)
        
        data = load_data()
        rooms = data['rooms']
        
        # Применяем фильтры
        filtered_rooms = apply_filters(rooms)
        
        # Обновляем список гостиниц
        load_hotels_list()
        
        # Заполняем таблицу
        for r in filtered_rooms:
            status_text = "🟢 Свободен" if r['status'] == "available" else "🔴 Забронирован"
            booked_by = r.get('booked_by', '') or ""
            
            # Определяем действие для кнопки
            if r['status'] == "available":
                action_text = "✅ Забронировать"
            elif r.get('booked_by') == client_user['login']:
                action_text = "❌ Отменить"
            else:
                action_text = "⏳ Занят"
            
            tree.insert('', 'end', values=(
                r['hotel'], 
                r['room_id'], 
                status_text, 
                booked_by,
                action_text
            ))
        
        # Обновляем статистику
        total_rooms = len(rooms)
        available_rooms = len([r for r in rooms if r['status'] == "available"])
        my_bookings = len([r for r in rooms if r.get('booked_by') == client_user['login']])
        filtered_count = len(filtered_rooms)
        
        stats_text = f"📊 Статистика: Всего номеров: {total_rooms} | 🟢 Свободно: {available_rooms} | 📖 Мои брони: {my_bookings} | 🔍 Найдено: {filtered_count}"
        stats_label.config(text=stats_text)

    def book_selected_room():
        """Бронирует выбранный номер"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите номер для бронирования!")
            return
            
        item = selected[0]
        values = tree.item(item)['values']
        
        if len(values) < 5:
            messagebox.showerror("Ошибка", "Не удалось получить данные о номере!")
            return
            
        hotel, room_id, status, booked_by, action = values
        
        print(f"DEBUG: Бронирование - Отель: {hotel}, Номер: {room_id}, Статус: {status}")
        
        if "🟢 Свободен" not in status:
            messagebox.showerror("Ошибка", "Этот номер уже забронирован!")
            return
        
        # Подтверждение бронирования
        if messagebox.askyesno("Подтверждение бронирования", 
                             f"Забронировать номер {room_id} в гостинице '{hotel}'?\n\n"
                             f"После подтверждения номер будет закреплен за вами."):
            data = load_data()
            room_found = False
            
            for r in data['rooms']:
                if r['hotel'] == hotel and r['room_id'] == room_id:
                    if r['status'] == 'available':
                        r['status'] = 'booked'
                        r['booked_by'] = client_user['login']
                        room_found = True
                        break
                    else:
                        messagebox.showerror("Ошибка", "Номер уже занят!")
                        return
            
            if not room_found:
                messagebox.showerror("Ошибка", "Номер не найден в базе данных!")
                return
            
            save_data(data)
            refresh_rooms()
            messagebox.showinfo("Успех!", 
                              f"✅ Номер {room_id} в гостинице '{hotel}' успешно забронирован!\n\n"
                              f"Вы можете отменить бронирование в любое время.")

    def cancel_booking():
        """Отменяет бронирование выбранного номера"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите номер для отмены бронирования!")
            return
            
        item = selected[0]
        values = tree.item(item)['values']
        
        if len(values) < 5:
            messagebox.showerror("Ошибка", "Не удалось получить данные о номере!")
            return
            
        hotel, room_id, status, booked_by, action = values
        
        print(f"DEBUG: Отмена брони - Отель: {hotel}, Номер: {room_id}, Забронирован: {booked_by}")
        
        if booked_by != client_user['login']:
            messagebox.showerror("Ошибка", "Вы можете отменять только свои бронирования!")
            return
        
        if messagebox.askyesno("Подтверждение отмены", 
                             f"Отменить бронирование номера {room_id} в гостинице '{hotel}'?\n\n"
                             f"После отмены номер станет доступен для бронирования другими."):
            data = load_data()
            room_found = False
            
            for r in data['rooms']:
                if r['hotel'] == hotel and r['room_id'] == room_id:
                    if r.get('booked_by') == client_user['login']:
                        r['status'] = 'available'
                        r['booked_by'] = None
                        room_found = True
                        break
            
            if not room_found:
                messagebox.showerror("Ошибка", "Бронирование не найдено!")
                return
            
            save_data(data)
            refresh_rooms()
            messagebox.showinfo("Успех!", "✅ Бронирование отменено!\n\nНомер теперь доступен для бронирования.")

    def show_my_bookings():
        """Показывает только бронирования текущего пользователя"""
        hotel_var.set("Все гостиницы")
        status_var.set("Забронирован")
        room_id_var.set("")
        refresh_rooms()
        messagebox.showinfo("Мои бронирования", 
                          "🔍 Показаны все ваши бронирования.\n"
                          "Используйте фильтры для уточнения поиска.")

    def on_double_click(event):
        """Обработчик двойного клика по строке"""
        item = tree.identify('item', event.x, event.y)
        if item:
            tree.selection_set(item)
            values = tree.item(item)['values']
            
            if len(values) < 5:
                return
                
            hotel, room_id, status, booked_by, action = values
            
            if "✅ Забронировать" in action:
                book_selected_room()
            elif "❌ Отменить" in action:
                cancel_booking()

    def show_context_menu(event):
        """Показывает контекстное меню"""
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def show_tooltip(event):
        """Показывает подсказку для элементов"""
        item = tree.identify('item', event.x, event.y)
        if item:
            col = tree.identify_column(event.x)
            values = tree.item(item)['values']
            
            if len(values) >= 5:
                hotel, room_id, status, booked_by, action = values
                
                if col == '#5':  # Колонка действий
                    if "✅ Забронировать" in action:
                        tooltip_text = "Двойной клик для бронирования"
                    elif "❌ Отменить" in action:
                        tooltip_text = "Двойной клик для отмены брони"
                    else:
                        tooltip_text = "Номер занят другим пользователем"
                    
                    # Создаем всплывающую подсказку
                    tooltip = tk.Toplevel(win)
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                    label = tk.Label(tooltip, text=tooltip_text, background="yellow", 
                                   relief='solid', borderwidth=1, font=('Arial', 8))
                    label.pack()
                    
                    # Удаляем подсказку через 2 секунды
                    tooltip.after(2000, tooltip.destroy)

    # ТЕПЕРЬ СОЗДАЕМ ЭЛЕМЕНТЫ ИНТЕРФЕЙСА

    # Заголовок
    header_frame = tk.Frame(win, bg='#e6f2ff', pady=15)
    header_frame.pack(fill='x', padx=10, pady=5)
    
    tk.Label(header_frame, text="🎯 Система бронирования номеров", 
             font=('Arial', 18, 'bold'), bg='#e6f2ff', fg='#2c3e50').pack()
    tk.Label(header_frame, text=f"👤 Добро пожаловать, {client_user['login']}!", 
             font=('Arial', 12), bg='#e6f2ff', fg='#34495e').pack()

    # Панель фильтров
    filter_frame = tk.LabelFrame(win, text="🔍 Фильтры поиска", font=('Arial', 11, 'bold'), 
                                padx=15, pady=15, bg='#f8f9fa')
    filter_frame.pack(fill='x', padx=15, pady=10)

    # Сетка для фильтров
    filter_grid = tk.Frame(filter_frame, bg='#f8f9fa')
    filter_grid.pack(fill='x')

    # Строка 1: Основные фильтры
    tk.Label(filter_grid, text="🏨 Гостиница:", bg='#f8f9fa', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
    hotel_var = tk.StringVar(value="Все гостиницы")
    hotel_combo = ttk.Combobox(filter_grid, textvariable=hotel_var, width=25, font=('Arial', 10))
    hotel_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    tk.Label(filter_grid, text="📊 Статус:", bg='#f8f9fa', font=('Arial', 10)).grid(row=0, column=2, padx=15, pady=5, sticky='w')
    status_var = tk.StringVar(value="Свободен")
    status_combo = ttk.Combobox(filter_grid, textvariable=status_var, 
                               values=["Свободен", "Забронирован", "Все"], width=15, font=('Arial', 10))
    status_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    # Строка 2: Дополнительные фильтры
    tk.Label(filter_grid, text="🔢 ID номера:", bg='#f8f9fa', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
    room_id_var = tk.StringVar()
    room_id_entry = tk.Entry(filter_grid, textvariable=room_id_var, width=20, font=('Arial', 10))
    room_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    # Кнопка сброса
    tk.Button(filter_grid, text="🔄 Сбросить фильтры", command=reset_filters, 
              bg='#e74c3c', fg='white', font=('Arial', 10), width=15).grid(row=1, column=3, padx=15, pady=5, sticky='e')

    # Пустая колонка для выравнивания
    filter_grid.columnconfigure(2, weight=1)

    # Статистика
    stats_frame = tk.Frame(win, bg='#ecf0f1', pady=8)
    stats_frame.pack(fill='x', padx=15, pady=5)
    
    stats_label = tk.Label(stats_frame, text="", font=('Arial', 10, 'bold'), bg='#ecf0f1', fg='#2c3e50')
    stats_label.pack()

    # Таблица номеров
    table_frame = tk.LabelFrame(win, text="📋 Доступные номера", font=('Arial', 11, 'bold'), padx=10, pady=10)
    table_frame.pack(fill='both', expand=True, padx=15, pady=10)

    # Создаем Treeview с прокруткой
    tree_frame = tk.Frame(table_frame)
    tree_frame.pack(fill='both', expand=True)

    tree_scroll_y = tk.Scrollbar(tree_frame)
    tree_scroll_y.pack(side='right', fill='y')

    tree_scroll_x = tk.Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side='bottom', fill='x')

    tree = ttk.Treeview(tree_frame, 
                        columns=("Hotel", "RoomID", "Status", "BookedBy", "Actions"), 
                        show="headings", 
                        yscrollcommand=tree_scroll_y.set,
                        xscrollcommand=tree_scroll_x.set,
                        height=15)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Настраиваем колонки
    columns = {
        "Hotel": ("🏨 Гостиница", 250),
        "RoomID": ("🔢 ID Номера", 120),
        "Status": ("📊 Статус", 120),
        "BookedBy": ("👤 Забронирован кем", 180),
        "Actions": ("⚡ Действия", 150)
    }

    for col, (text, width) in columns.items():
        tree.heading(col, text=text)
        tree.column(col, width=width, anchor='center')

    tree.pack(fill='both', expand=True)

    # Панель управления
    control_frame = tk.Frame(win, bg='#f8f9fa', pady=10)
    control_frame.pack(fill='x', padx=15, pady=10)

    # Кнопки управления
    button_frame = tk.Frame(control_frame, bg='#f8f9fa')
    button_frame.pack()

    buttons = [
        ("🔄 Обновить список", refresh_rooms, '#3498db'),
        ("✅ Забронировать", book_selected_room, '#27ae60'),
        ("❌ Отменить бронь", cancel_booking, '#e74c3c'),
        ("📖 Мои бронирования", show_my_bookings, '#9b59b6')
    ]

    for text, command, color in buttons:
        tk.Button(button_frame, text=text, command=command, 
                 bg=color, fg='white', font=('Arial', 10), 
                 width=18, height=1).pack(side='left', padx=5)

    # Привязываем обработчики событий
    tree.bind('<Double-1>', on_double_click)
    
    # Привязываем обновление при изменении фильтров
    hotel_combo.bind('<<ComboboxSelected>>', lambda e: refresh_rooms())
    status_combo.bind('<<ComboboxSelected>>', lambda e: refresh_rooms())
    room_id_entry.bind('<KeyRelease>', lambda e: refresh_rooms())

    # Создаем контекстное меню
    context_menu = tk.Menu(win, tearoff=0, font=('Arial', 10))
    context_menu.add_command(label="✅ Забронировать", command=book_selected_room)
    context_menu.add_command(label="❌ Отменить бронь", command=cancel_booking)
    context_menu.add_separator()
    context_menu.add_command(label="🔄 Обновить", command=refresh_rooms)

    tree.bind('<Button-3>', show_context_menu)
    tree.bind('<Motion>', show_tooltip)

    # Загружаем данные при запуске
    refresh_rooms()
    center_window(win)
# ------------------- ГЛАВНОЕ ОКНО -------------------
def main():
    root = tk.Tk()
    root.title("Система бронирования турфирмы")
    root.geometry("500x300")

    # Центрирование главного окна
    root.eval('tk::PlaceWindow . center')

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=50, pady=50)

    tk.Label(main_frame, text="Система бронирования турфирмы", 
             font=('Arial', 16, 'bold')).pack(pady=30)
    
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Вход", command=lambda: login_window(root), 
              width=20, height=2, bg='lightblue').pack(pady=10)
              
    tk.Button(button_frame, text="Регистрация", command=lambda: register_window(root), 
              width=20, height=2, bg='lightgreen').pack(pady=10)

    # Статус базы данных
    data = load_data()
    status_text = f"Всего пользователей: {len(data['users'])} | Гостиниц: {len(data['hotels'])} | Номеров: {len(data['rooms'])}"
    tk.Label(main_frame, text=status_text, font=('Arial', 8)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()