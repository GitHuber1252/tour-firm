import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkinter import font as tkFont
from datetime import datetime, timedelta

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, 'database.json')
BOOKINGS_FILE = os.path.join(BASE_DIR, 'bookings.json')

# Стилизация
STYLES = {
    'bg_color': '#f5f6fa',
    'card_bg': '#ffffff',
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    'text_dark': '#2c3e50',
    'text_light': '#7f8c8d'
}

def setup_styles():
    style = ttk.Style()
    style.configure('TFrame', background=STYLES['bg_color'])
    style.configure('TLabel', background=STYLES['bg_color'], foreground=STYLES['text_dark'])
    style.configure('TButton', font=('Arial', 10))
    style.configure('Primary.TButton', background=STYLES['primary'], foreground='white')
    style.configure('Success.TButton', background=STYLES['secondary'], foreground='white')
    style.configure('Danger.TButton', background=STYLES['danger'], foreground='white')
    style.configure('TCombobox', font=('Arial', 10))
    style.configure('Treeview', font=('Arial', 9), rowheight=25)
    style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background=STYLES['light'])

def create_card(parent, **kwargs):
    card = tk.Frame(parent, bg=STYLES['card_bg'], relief='raised', bd=1, **kwargs)
    return card

def create_header(parent, text, size=16):
    header = tk.Label(parent, text=text, font=('Arial', size, 'bold'), 
                     bg=STYLES['bg_color'], fg=STYLES['dark'])
    return header

def create_button(parent, text, command, style='default', width=15, height=1, font_size=10):
    bg_colors = {
        'default': STYLES['primary'],
        'success': STYLES['secondary'],
        'danger': STYLES['danger'],
        'warning': STYLES['warning']
    }
    
    bg_color = bg_colors.get(style, STYLES['primary'])
    btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg='white',
                   font=('Arial', font_size, 'bold'), relief='raised', bd=2,
                   width=width, height=height)
    return btn

# ------------------- ФУНКЦИИ РАБОТЫ С ДАННЫМИ -------------------
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

def load_bookings():
    default_data = {"bookings": [], "cancel_requests": []}

    if not os.path.exists(BOOKINGS_FILE):
        save_bookings(default_data)
        return default_data

    try:
        with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        save_bookings(default_data)
        return default_data

    if "bookings" not in data:
        data["bookings"] = []
    if "cancel_requests" not in data:
        data["cancel_requests"] = []

    return data

def save_bookings(data):
    try:
        with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения bookings: {e}")
        return False

def center_window(window):
    """Центрирует окно на экране"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def create_test_data():
    """Создает тестовые данные если база пустая"""
    data = load_data()
    
    if not data['users']:
        # Создаем администратора
        data['users'].append({
            "login": "admin",
            "password": "admin",
            "role": "admin"
        })
        
        # Создаем тестовую гостиницу
        data['hotels'].append({
            "id": "1",
            "name": "Гостиница Москва",
            "rooms": []
        })
        
        # Создаем пользователя гостиницы
        data['users'].append({
            "login": "hotel1",
            "password": "password",
            "role": "hotel",
            "hotel_id": "1",
            "hotel_name": "Гостиница Москва"
        })
        
        # Создаем номера
        data['rooms'].append({
            "hotel": "Гостиница Москва",
            "hotel_id": "1",
            "room_id": "101",
            "capacity": 2,
            "price": 2500,
            "status": "available"
        })
        
        data['rooms'].append({
            "hotel": "Гостиница Москва",
            "hotel_id": "1",
            "room_id": "102",
            "capacity": 3,
            "price": 3500,
            "status": "available"
        })
        
        data['rooms'].append({
            "hotel": "Гостиница Москва",
            "hotel_id": "1",
            "room_id": "201",
            "capacity": 4,
            "price": 5000,
            "status": "available"
        })
        
        # Создаем клиента
        data['users'].append({
            "login": "user1",
            "password": "password",
            "role": "client"
        })
        
        save_data(data)
        print("Тестовые данные созданы!")

# ------------------- ФУНКЦИИ БРОНИРОВАНИЯ -------------------
def is_room_available(hotel_id, room_id, check_in, check_out):
    """Проверяет доступность номера на указанные даты"""
    bookings_data = load_bookings()
    
    # Преобразуем даты в datetime объекты
    new_check_in = datetime.strptime(check_in, '%Y-%m-%d')
    new_check_out = datetime.strptime(check_out, '%Y-%m-%d')
    
    for booking in bookings_data['bookings']:
        if (booking['hotel_id'] == hotel_id and 
            str(booking['room_id']) == str(room_id) and 
            booking['status'] in ['на рассмотрении', 'подтверждена']):
            
            # Преобразуем даты существующего бронирования
            existing_check_in = datetime.strptime(booking['check_in'], '%Y-%m-%d')
            existing_check_out = datetime.strptime(booking['check_out'], '%Y-%m-%d')
            
            # Проверяем пересечение дат
            if (new_check_in < existing_check_out and new_check_out > existing_check_in):
                return False
    
    return True

def create_booking(hotel_id, room_id, user_login, check_in, check_out, guests, price):
    """Создает новое бронирование"""
    bookings_data = load_bookings()
    
    # Генерируем ID брони
    booking_id = str(len(bookings_data['bookings']) + 1)
    
    new_booking = {
        "booking_id": booking_id,
        "hotel_id": hotel_id,
        "room_id": room_id,
        "user_login": user_login,
        "check_in": check_in,
        "check_out": check_out,
        "status": "на рассмотрении",
        "created_at": datetime.now().strftime('%Y-%m-%d'),
        "price": price,
        "guests": guests
    }
    
    bookings_data['bookings'].append(new_booking)
    if save_bookings(bookings_data):
        return booking_id
    else:
        return None

def update_booking_status(booking_id, new_status):
    """Обновляет статус бронирования"""
    bookings_data = load_bookings()
    updated = False
    
    for booking in bookings_data['bookings']:
        if booking['booking_id'] == str(booking_id):
            booking['status'] = new_status
            updated = True
            break
    
    if updated:
        if save_bookings(bookings_data):
            print(f"Статус бронирования {booking_id} изменен на: {new_status}")
            return True
        else:
            print(f"Ошибка сохранения статуса бронирования {booking_id}")
            return False
    else:
        print(f"Бронирование {booking_id} не найдено")
        return False

def create_cancel_request(booking_id, user_login, reason=""):
    """Создает запрос на отмену бронирования"""
    bookings_data = load_bookings()
    
    request_id = str(len(bookings_data['cancel_requests']) + 1)
    
    new_request = {
        "request_id": request_id,
        "booking_id": booking_id,
        "user_login": user_login,
        "reason": reason,
        "status": "ожидает рассмотрения",
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    bookings_data['cancel_requests'].append(new_request)
    if save_bookings(bookings_data):
        return request_id
    else:
        return None

def update_cancel_request_status(request_id, new_status):
    """Обновляет статус запроса на отмену"""
    bookings_data = load_bookings()
    updated = False
    
    for request in bookings_data['cancel_requests']:
        if request['request_id'] == str(request_id):
            request['status'] = new_status
            updated = True
            break
    
    if updated:
        if save_bookings(bookings_data):
            print(f"Статус запроса {request_id} изменен на: {new_status}")
            return True
        else:
            print(f"Ошибка сохранения статуса запроса {request_id}")
            return False
    else:
        print(f"Запрос {request_id} не найден")
        return False

def get_pending_cancel_requests():
    """Возвращает ожидающие запросы на отмену"""
    bookings_data = load_bookings()
    return [r for r in bookings_data['cancel_requests'] if r['status'] == 'ожидает рассмотрения']

def get_user_bookings(user_login):
    """Возвращает бронирования пользователя"""
    bookings_data = load_bookings()
    return [b for b in bookings_data['bookings'] if b['user_login'] == user_login]

def get_hotel_bookings(hotel_id):
    """Возвращает бронирования гостиницы"""
    bookings_data = load_bookings()
    return [b for b in bookings_data['bookings'] if b['hotel_id'] == hotel_id]

def get_all_bookings():
    """Возвращает все бронирования"""
    bookings_data = load_bookings()
    return bookings_data['bookings']

# ------------------- ФУНКЦИИ КЛИЕНТА -------------------
def client_window(root, client_user):
    win = tk.Toplevel(root)
    win.title("Система бронирования номеров")
    win.geometry("1400x700")
    win.configure(bg=STYLES['bg_color'])
    win.transient(root)
    win.grab_set()

    # Заголовок
    header_frame = tk.Frame(win, bg=STYLES['bg_color'], pady=15)
    header_frame.pack(fill='x', padx=20, pady=10)
    
    create_header(header_frame, "🎯 Система бронирования номеров", 18).pack()
    tk.Label(header_frame, text=f"👤 Добро пожаловать, {client_user['login']}!", 
             font=('Arial', 12), bg=STYLES['bg_color'], fg=STYLES['text_light']).pack()

    # Создаем Notebook для вкладок
    notebook = ttk.Notebook(win)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # Вкладка 1: Бронирование номеров
    booking_frame = ttk.Frame(notebook)
    notebook.add(booking_frame, text="🛎️ Бронирование номеров")

    # Вкладка 2: Мои бронирования
    my_bookings_frame = ttk.Frame(notebook)
    notebook.add(my_bookings_frame, text="📋 Мои бронирования")

    # === ВКЛАДКА БРОНИРОВАНИЯ ===
    # Фильтры для поиска
    filter_frame = create_card(booking_frame, padx=15, pady=15)
    filter_frame.pack(fill='x', padx=10, pady=10)

    tk.Label(filter_frame, text="🔍 Поиск номеров", font=('Arial', 12, 'bold'), 
            bg=STYLES['card_bg']).pack(anchor='w', pady=(0, 10))

    filter_grid = tk.Frame(filter_frame, bg=STYLES['card_bg'])
    filter_grid.pack(fill='x')

    # Даты бронирования
    tk.Label(filter_grid, text="Дата заезда:", bg=STYLES['card_bg']).grid(row=0, column=0, sticky='w', padx=5, pady=5)
    check_in_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    check_in_entry = tk.Entry(filter_grid, textvariable=check_in_var, width=12)
    check_in_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_grid, text="Дата выезда:", bg=STYLES['card_bg']).grid(row=0, column=2, sticky='w', padx=5, pady=5)
    check_out_var = tk.StringVar(value=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
    check_out_entry = tk.Entry(filter_grid, textvariable=check_out_var, width=12)
    check_out_entry.grid(row=0, column=3, padx=5, pady=5)

    # Количество гостей
    tk.Label(filter_grid, text="Гостей:", bg=STYLES['card_bg']).grid(row=0, column=4, sticky='w', padx=5, pady=5)
    guests_var = tk.StringVar(value="1")
    guests_combo = ttk.Combobox(filter_grid, textvariable=guests_var, values=[str(i) for i in range(1, 11)], width=5)
    guests_combo.grid(row=0, column=5, padx=5, pady=5)

    # Кнопка поиска
    search_btn = create_button(filter_grid, "🔍 Найти номера", lambda: refresh_available_rooms(), 'primary', width=15)
    search_btn.grid(row=0, column=6, padx=10, pady=5)

    # Таблица доступных номеров
    table_frame = create_card(booking_frame)
    table_frame.pack(fill='both', expand=True, padx=10, pady=10)

    available_tree = ttk.Treeview(table_frame, columns=("Hotel", "RoomID", "Capacity", "Price", "Actions"), show="headings")
    available_tree.heading("Hotel", text="🏨 Гостиница")
    available_tree.heading("RoomID", text="🔢 ID Номера")
    available_tree.heading("Capacity", text="👥 Вместимость")
    available_tree.heading("Price", text="💰 Стоимость/ночь")
    available_tree.heading("Actions", text="⚡ Действия")
    available_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_available_rooms():
        """Обновляет список доступных номеров"""
        available_tree.delete(*available_tree.get_children())
        data = load_data()
        
        check_in = check_in_var.get()
        check_out = check_out_var.get()
        guests = int(guests_var.get())
        
        # Валидация дат
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
            
            if check_in_date >= check_out_date:
                messagebox.showerror("Ошибка", "Дата выезда должна быть позже даты заезда!")
                return
                
            if check_in_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                messagebox.showerror("Ошибка", "Нельзя бронировать на прошедшие даты!")
                return
                
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте YYYY-MM-DD")
            return
        
        found_rooms = 0
        for room in data['rooms']:
            # Находим название гостиницы по ID
            hotel_name = next((h['name'] for h in data['hotels'] if h['id'] == room['hotel_id']), "Неизвестно")
            
            # Проверяем вместимость
            if room.get('capacity', 1) >= guests:
                # Проверяем доступность на даты
                if is_room_available(room['hotel_id'], room['room_id'], check_in, check_out):
                    available_tree.insert('', 'end', values=(
                        hotel_name,
                        room['room_id'],
                        room.get('capacity', 1),
                        f"{room.get('price', 1000)} руб.",
                        "✅ Забронировать"
                    ))
                    found_rooms += 1
        
        if found_rooms == 0:
            messagebox.showinfo("Информация", "Нет доступных номеров по вашим критериям поиска.")

    def book_selected_room():
        """Бронирует выбранный номер"""
        selected = available_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите номер для бронирования!")
            return
            
        item = selected[0]
        values = available_tree.item(item)['values']
        hotel_name, room_id, capacity, price_str, action = values
        
        # Получаем данные о номере
        data = load_data()
        
        # Находим гостиницу по названию
        hotel_data = next((h for h in data['hotels'] if h['name'] == hotel_name), None)
        if not hotel_data:
            messagebox.showerror("Ошибка", f"Гостиница '{hotel_name}' не найдена!")
            return
        
        # Находим номер по ID гостиницы и ID номера
        room_data = next((r for r in data['rooms'] 
                         if r['hotel_id'] == hotel_data['id'] and str(r['room_id']) == str(room_id)), None)
        
        if not room_data:
            messagebox.showerror("Ошибка", f"Номер {room_id} в гостинице '{hotel_name}' не найден!")
            return
        
        check_in = check_in_var.get()
        check_out = check_out_var.get()
        guests = int(guests_var.get())
        
        # Проверяем доступность номера еще раз
        if not is_room_available(hotel_data['id'], room_id, check_in, check_out):
            messagebox.showerror("Ошибка", "Этот номер больше не доступен на выбранные даты!")
            refresh_available_rooms()
            return
        
        price = room_data.get('price', 1000)
        
        # Рассчитываем количество ночей и общую стоимость
        nights = (datetime.strptime(check_out, '%Y-%m-%d') - datetime.strptime(check_in, '%Y-%m-%d')).days
        total_price = price * nights
        
        # Подтверждение бронирования
        if messagebox.askyesno("Подтверждение бронирования", 
                             f"Забронировать номер {room_id} в гостинице '{hotel_name}'?\n"
                             f"Даты: {check_in} - {check_out} ({nights} ночей)\n"
                             f"Гостей: {guests}\n"
                             f"Стоимость: {total_price} руб."):
            
            # Создаем бронирование
            booking_id = create_booking(
                hotel_data['id'],
                room_id,
                client_user['login'],
                check_in,
                check_out,
                guests,
                price
            )
            
            if booking_id:
                messagebox.showinfo("Успех", 
                                  f"Бронирование #{booking_id} создано!\n"
                                  f"Статус: на рассмотрении\n"
                                  f"Ожидайте подтверждения от администратора.")
                refresh_available_rooms()
                refresh_my_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать бронирование!")

    # Кнопки управления
    control_frame = tk.Frame(booking_frame, bg=STYLES['bg_color'])
    control_frame.pack(fill='x', padx=20, pady=10)

    create_button(control_frame, "✅ Забронировать выбранный", book_selected_room, 'success').pack(side='left', padx=5)
    create_button(control_frame, "🔄 Обновить", refresh_available_rooms, 'default').pack(side='left', padx=5)

    # === ВКЛАДКА МОИ БРОНИРОВАНИЯ ===
    my_bookings_tree = ttk.Treeview(my_bookings_frame, 
                                   columns=("ID", "Hotel", "Room", "CheckIn", "CheckOut", "Guests", "Price", "Status"), 
                                   show="headings")
    my_bookings_tree.heading("ID", text="🔑 ID Брони")
    my_bookings_tree.heading("Hotel", text="🏨 Гостиница")
    my_bookings_tree.heading("Room", text="🔢 Номер")
    my_bookings_tree.heading("CheckIn", text="📅 Заезд")
    my_bookings_tree.heading("CheckOut", text="📅 Выезд")
    my_bookings_tree.heading("Guests", text="👥 Гости")
    my_bookings_tree.heading("Price", text="💰 Стоимость")
    my_bookings_tree.heading("Status", text="📊 Статус")
    
    # Настройка колонок
    my_bookings_tree.column("ID", width=80)
    my_bookings_tree.column("Hotel", width=150)
    my_bookings_tree.column("Room", width=80)
    my_bookings_tree.column("CheckIn", width=100)
    my_bookings_tree.column("CheckOut", width=100)
    my_bookings_tree.column("Guests", width=80)
    my_bookings_tree.column("Price", width=120)
    my_bookings_tree.column("Status", width=150)
    
    my_bookings_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_my_bookings():
        """Обновляет список бронирований пользователя"""
        my_bookings_tree.delete(*my_bookings_tree.get_children())
        data = load_data()
        user_bookings = get_user_bookings(client_user['login'])
        
        for booking in user_bookings:
            # Находим информацию о гостинице и номере
            hotel_name = next((h['name'] for h in data['hotels'] if h['id'] == booking['hotel_id']), "Неизвестно")
            
            total_price = booking['price'] * ((datetime.strptime(booking['check_out'], '%Y-%m-%d') - 
                                            datetime.strptime(booking['check_in'], '%Y-%m-%d')).days)
            
            # Определяем цвет статуса
            status = booking['status']
            status_display = status
            
            my_bookings_tree.insert('', 'end', values=(
                booking['booking_id'],
                hotel_name,
                booking['room_id'],
                booking['check_in'],
                booking['check_out'],
                booking['guests'],
                f"{total_price} руб.",
                status_display
            ))

    def cancel_my_booking():
        """Запрос на отмену бронирования"""
        selected = my_bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите бронирование для отмены!")
            return
            
        booking_id = my_bookings_tree.item(selected[0])['values'][0]
        status = my_bookings_tree.item(selected[0])['values'][7]
        
        if status == 'отменена':
            messagebox.showwarning("Внимание", "Это бронирование уже отменено!")
            return
            
        if status == 'завершена':
            messagebox.showwarning("Внимание", "Нельзя отменить завершенное бронирование!")
            return
            
        reason = simpledialog.askstring("Причина отмены", "Укажите причину отмены бронирования:")
        if reason is None:
            return
            
        if messagebox.askyesno("Запрос отмены", 
                             f"Отправить запрос на отмену бронирования #{booking_id}?\n"
                             f"Причина: {reason}"):
            # Создаем запрос на отмену
            request_id = create_cancel_request(booking_id, client_user['login'], reason)
            if request_id:
                messagebox.showinfo("Запрос отправлен", 
                                  f"Ваш запрос на отмену #{request_id} отправлен администратору.")
                refresh_my_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать запрос на отмену!")

    my_bookings_control = tk.Frame(my_bookings_frame, bg=STYLES['bg_color'])
    my_bookings_control.pack(fill='x', padx=20, pady=10)

    create_button(my_bookings_control, "❌ Запрос отмены", cancel_my_booking, 'danger').pack(side='left', padx=5)
    create_button(my_bookings_control, "🔄 Обновить", refresh_my_bookings, 'default').pack(side='left', padx=5)

    # Загружаем начальные данные
    refresh_available_rooms()
    refresh_my_bookings()
    center_window(win)

# ------------------- ФУНКЦИИ ГОСТИНИЦЫ -------------------
def hotel_window(root, hotel_user):
    win = tk.Toplevel(root)
    win.title(f"Управление гостиницей: {hotel_user.get('hotel_name', '')}")
    win.geometry("1200x700")
    win.configure(bg=STYLES['bg_color'])
    win.transient(root)
    win.grab_set()

    header_frame = tk.Frame(win, bg=STYLES['bg_color'])
    header_frame.pack(pady=15)

    create_header(header_frame, f"🏨 {hotel_user.get('hotel_name', '')}", 18).pack()
    tk.Label(header_frame, text=f"ID: {hotel_user.get('hotel_id', '')} | Управление гостиницей", 
             font=('Arial', 12), bg=STYLES['bg_color'], fg=STYLES['text_light']).pack()

    # Создаем Notebook для вкладок
    notebook = ttk.Notebook(win)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # Вкладка 1: Управление номерами
    rooms_frame = ttk.Frame(notebook)
    notebook.add(rooms_frame, text="🛏️ Управление номерами")

    # Вкладка 2: Бронирования
    bookings_frame = ttk.Frame(notebook)
    notebook.add(bookings_frame, text="📋 Бронирования")

    # === ВКЛАДКА УПРАВЛЕНИЕ НОМЕРАМИ ===
    rooms_tree = ttk.Treeview(rooms_frame, columns=("RoomID", "Capacity", "Price", "Status"), show="headings")
    rooms_tree.heading("RoomID", text="🔢 ID Номера")
    rooms_tree.heading("Capacity", text="👥 Вместимость")
    rooms_tree.heading("Price", text="💰 Стоимость/ночь")
    rooms_tree.heading("Status", text="📊 Статус")
    rooms_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_rooms():
        """Обновляет список номеров гостиницы"""
        rooms_tree.delete(*rooms_tree.get_children())
        data = load_data()
        hotel_rooms = [r for r in data['rooms'] if r['hotel_id'] == hotel_user['hotel_id']]
        
        for room in hotel_rooms:
            # Проверяем доступность номера
            is_available = is_room_available(room['hotel_id'], room['room_id'], 
                                           datetime.now().strftime('%Y-%m-%d'),
                                           (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
            status = "🟢 Свободен" if is_available else "🔴 Занят"
            
            rooms_tree.insert('', 'end', values=(
                room['room_id'],
                room.get('capacity', 1),
                f"{room.get('price', 1000)} руб.",
                status
            ))

    def add_room():
        """Добавляет новый номер"""
        add_win = tk.Toplevel(win)
        add_win.title("Добавление номера")
        add_win.geometry("400x300")
        add_win.configure(bg=STYLES['bg_color'])
        
        header_frame = tk.Frame(add_win, bg=STYLES['bg_color'])
        header_frame.pack(pady=10)
        create_header(header_frame, "Добавление номера", 14).pack()
        
        form_frame = create_card(add_win, padx=20, pady=15)
        form_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # ID номера
        tk.Label(form_frame, text="ID номера:", bg=STYLES['card_bg'], 
                font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10, padx=5)
        room_id_entry = tk.Entry(form_frame, width=20, font=('Arial', 10))
        room_id_entry.grid(row=0, column=1, pady=10, padx=5, sticky='ew')
        
        # Вместимость
        tk.Label(form_frame, text="Вместимость:", bg=STYLES['card_bg'], 
                font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10, padx=5)
        capacity_var = tk.StringVar(value="1")
        capacity_combo = ttk.Combobox(form_frame, textvariable=capacity_var, 
                                    values=[str(i) for i in range(1, 11)], width=18)
        capacity_combo.grid(row=1, column=1, pady=10, padx=5, sticky='ew')
        
        # Стоимость
        tk.Label(form_frame, text="Стоимость/ночь:", bg=STYLES['card_bg'], 
                font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10, padx=5)
        price_entry = tk.Entry(form_frame, width=20, font=('Arial', 10))
        price_entry.insert(0, "1000")
        price_entry.grid(row=2, column=1, pady=10, padx=5, sticky='ew')

        form_frame.columnconfigure(1, weight=1)

        def do_add():
            room_id = room_id_entry.get().strip()
            capacity = capacity_var.get()
            price = price_entry.get().strip()
            
            if not room_id or not capacity or not price:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
                
            try:
                price = int(price)
                capacity = int(capacity)
            except ValueError:
                messagebox.showerror("Ошибка", "Стоимость и вместимость должны быть числами!")
                return
            
            data = load_data()
            
            # Проверяем, существует ли номер
            existing_room = next((r for r in data['rooms'] if r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id), None)
            if existing_room:
                messagebox.showerror("Ошибка", "Номер с таким ID уже существует!")
                return
                
            # Добавляем номер
            data['rooms'].append({
                "hotel": hotel_user['hotel_name'],
                "hotel_id": hotel_user['hotel_id'],
                "room_id": room_id,
                "capacity": capacity,
                "price": price,
                "status": "available"
            })
            
            save_data(data)
            messagebox.showinfo("Успех", f"Номер {room_id} добавлен!")
            add_win.destroy()
            refresh_rooms()

        button_frame = tk.Frame(add_win, bg=STYLES['bg_color'])
        button_frame.pack(pady=10)

        create_button(button_frame, "✅ Добавить номер", do_add, 'success', width=20).pack(pady=5)
        center_window(add_win)

    def delete_room():
        """Удаляет номер"""
        selected = rooms_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите номер для удаления!")
            return
            
        room_id = rooms_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить номер {room_id}?"):
            data = load_data()
            data['rooms'] = [r for r in data['rooms'] if not (r['hotel_id'] == hotel_user['hotel_id'] and r['room_id'] == room_id)]
            save_data(data)
            refresh_rooms()
            messagebox.showinfo("Успех", "Номер удален!")

    rooms_control = tk.Frame(rooms_frame, bg=STYLES['bg_color'])
    rooms_control.pack(fill='x', padx=20, pady=10)

    create_button(rooms_control, "➕ Добавить номер", add_room, 'success').pack(side='left', padx=5)
    create_button(rooms_control, "❌ Удалить номер", delete_room, 'danger').pack(side='left', padx=5)
    create_button(rooms_control, "🔄 Обновить", refresh_rooms, 'default').pack(side='left', padx=5)

    # === ВКЛАДКА БРОНИРОВАНИЯ ===
    bookings_tree = ttk.Treeview(bookings_frame, 
                                columns=("ID", "Room", "User", "CheckIn", "CheckOut", "Guests", "Price", "Status"), 
                                show="headings")
    bookings_tree.heading("ID", text="🔑 ID Брони")
    bookings_tree.heading("Room", text="🔢 Номер")
    bookings_tree.heading("User", text="👤 Клиент")
    bookings_tree.heading("CheckIn", text="📅 Заезд")
    bookings_tree.heading("CheckOut", text="📅 Выезд")
    bookings_tree.heading("Guests", text="👥 Гости")
    bookings_tree.heading("Price", text="💰 Стоимость")
    bookings_tree.heading("Status", text="📊 Статус")
    
    # Настройка колонок
    bookings_tree.column("ID", width=80)
    bookings_tree.column("Room", width=80)
    bookings_tree.column("User", width=120)
    bookings_tree.column("CheckIn", width=100)
    bookings_tree.column("CheckOut", width=100)
    bookings_tree.column("Guests", width=80)
    bookings_tree.column("Price", width=120)
    bookings_tree.column("Status", width=150)
    
    bookings_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_bookings():
        """Обновляет список бронирований гостиницы"""
        bookings_tree.delete(*bookings_tree.get_children())
        hotel_bookings = get_hotel_bookings(hotel_user['hotel_id'])
        
        for booking in hotel_bookings:
            total_price = booking['price'] * ((datetime.strptime(booking['check_out'], '%Y-%m-%d') - 
                                            datetime.strptime(booking['check_in'], '%Y-%m-%d')).days)
            
            bookings_tree.insert('', 'end', values=(
                booking['booking_id'],
                booking['room_id'],
                booking['user_login'],
                booking['check_in'],
                booking['check_out'],
                booking['guests'],
                f"{total_price} руб.",
                booking['status']
            ))

    def request_cancel_booking():
        """Запрос на отмену бронирования"""
        selected = bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите бронирование для отмены!")
            return
            
        booking_id = bookings_tree.item(selected[0])['values'][0]
        status = bookings_tree.item(selected[0])['values'][7]
        
        if status == 'отменена':
            messagebox.showwarning("Внимание", "Это бронирование уже отменено!")
            return
            
        reason = simpledialog.askstring("Причина отмены", "Укажите причину отмены бронирования:")
        if reason is None:
            return
            
        if messagebox.askyesno("Запрос отмены", 
                             f"Отправить запрос на отмену бронирования #{booking_id}?\n"
                             f"Причина: {reason}"):
            # Создаем запрос на отмену
            request_id = create_cancel_request(booking_id, hotel_user['login'], reason)
            if request_id:
                messagebox.showinfo("Запрос отправлен", 
                                  f"Запрос на отмену #{request_id} отправлен администратору.")
                refresh_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать запрос на отмену!")

    bookings_control = tk.Frame(bookings_frame, bg=STYLES['bg_color'])
    bookings_control.pack(fill='x', padx=20, pady=10)

    create_button(bookings_control, "❌ Запрос отмены", request_cancel_booking, 'danger').pack(side='left', padx=5)
    create_button(bookings_control, "🔄 Обновить", refresh_bookings, 'default').pack(side='left', padx=5)

    # Загружаем начальные данные
    refresh_rooms()
    refresh_bookings()
    center_window(win)

# ------------------- ФУНКЦИИ АДМИНИСТРАТОРА -------------------
def admin_window(root):
    win = tk.Toplevel(root)
    win.title("Панель администратора")
    win.geometry("1200x800")
    win.configure(bg=STYLES['bg_color'])
    win.transient(root)
    win.grab_set()

    header_frame = tk.Frame(win, bg=STYLES['bg_color'])
    header_frame.pack(pady=20)

    create_header(header_frame, "Панель администратора", 20).pack()
    tk.Label(header_frame, text="Управление системой бронирования", 
             font=('Arial', 12), bg=STYLES['bg_color'], fg=STYLES['text_light']).pack()

    # Создаем Notebook для вкладок
    notebook = ttk.Notebook(win)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # Вкладка 1: Управление гостиницами
    hotels_frame = ttk.Frame(notebook)
    notebook.add(hotels_frame, text="🏨 Гостиницы")

    # Вкладка 2: Управление бронированиями
    bookings_frame = ttk.Frame(notebook)
    notebook.add(bookings_frame, text="📋 Бронирования")

    # Вкладка 3: Запросы на отмену
    cancel_requests_frame = ttk.Frame(notebook)
    notebook.add(cancel_requests_frame, text="❌ Запросы на отмену")

    # Вкладка 4: Пользователи
    users_frame = ttk.Frame(notebook)
    notebook.add(users_frame, text="👥 Пользователи")

    # === ВКЛАДКА ГОСТИНИЦЫ ===
    hotels_tree = ttk.Treeview(hotels_frame, columns=("ID", "Name", "Rooms", "Owner"), show="headings")
    hotels_tree.heading("ID", text="ID")
    hotels_tree.heading("Name", text="Название гостиницы")
    hotels_tree.heading("Rooms", text="Количество номеров")
    hotels_tree.heading("Owner", text="Владелец")
    hotels_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_hotels():
        hotels_tree.delete(*hotels_tree.get_children())
        data = load_data()
        
        for h in data['hotels']:
            room_count = len([r for r in data['rooms'] if r['hotel_id'] == h['id']])
            owner = "Не назначен"
            for user in data['users']:
                if user.get('hotel_id') == h['id']:
                    owner = user['login']
                    break
            hotels_tree.insert('', 'end', values=(h['id'], h['name'], room_count, owner))

    def add_hotel():
        hotel_name = simpledialog.askstring("Добавление гостиницы", "Введите название гостиницы:")
        if not hotel_name:
            return

        data = load_data()
        hotel_id = str(len(data["hotels"]) + 1)
        
        data["hotels"].append({"id": hotel_id, "name": hotel_name, "rooms": []})
        
        hotel_login = f"hotel_{hotel_id}"
        hotel_password = "password123"
        
        data['users'].append({
            "login": hotel_login,
            "password": hotel_password,
            "role": "hotel",
            "hotel_id": hotel_id,
            "hotel_name": hotel_name
        })
        
        save_data(data)
        messagebox.showinfo("Успех", f"Гостиница '{hotel_name}' добавлена!\nID: {hotel_id}\nЛогин: {hotel_login}\nПароль: {hotel_password}")
        refresh_hotels()

    def delete_hotel():
        selected = hotels_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите гостиницу для удаления!")
            return
            
        hotel_id = hotels_tree.item(selected[0])['values'][0]
        hotel_name = hotels_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите удалить гостиницу '{hotel_name}'?"):
            data = load_data()
            data['hotels'] = [h for h in data['hotels'] if h['id'] != str(hotel_id)]
            data['rooms'] = [r for r in data['rooms'] if r['hotel_id'] != str(hotel_id)]
            data['users'] = [u for u in data['users'] if u.get('hotel_id') != str(hotel_id)]
            save_data(data)
            messagebox.showinfo("Успех", "Гостиница удалена!")
            refresh_hotels()

    hotels_control = tk.Frame(hotels_frame, bg=STYLES['bg_color'])
    hotels_control.pack(fill='x', padx=20, pady=10)

    create_button(hotels_control, "➕ Добавить гостиницу", add_hotel, 'success').pack(side='left', padx=5)
    create_button(hotels_control, "❌ Удалить гостиницу", delete_hotel, 'danger').pack(side='left', padx=5)
    create_button(hotels_control, "🔄 Обновить", refresh_hotels, 'default').pack(side='left', padx=5)

    # === ВКЛАДКА БРОНИРОВАНИЯ ===
    admin_bookings_tree = ttk.Treeview(bookings_frame, 
                                      columns=("ID", "Hotel", "Room", "User", "CheckIn", "CheckOut", "Guests", "Price", "Status"), 
                                      show="headings")
    admin_bookings_tree.heading("ID", text="🔑 ID Брони")
    admin_bookings_tree.heading("Hotel", text="🏨 Гостиница")
    admin_bookings_tree.heading("Room", text="🔢 Номер")
    admin_bookings_tree.heading("User", text="👤 Клиент")
    admin_bookings_tree.heading("CheckIn", text="📅 Заезд")
    admin_bookings_tree.heading("CheckOut", text="📅 Выезд")
    admin_bookings_tree.heading("Guests", text="👥 Гости")
    admin_bookings_tree.heading("Price", text="💰 Стоимость")
    admin_bookings_tree.heading("Status", text="📊 Статус")
    
    # Настройка колонок
    admin_bookings_tree.column("ID", width=80)
    admin_bookings_tree.column("Hotel", width=150)
    admin_bookings_tree.column("Room", width=80)
    admin_bookings_tree.column("User", width=120)
    admin_bookings_tree.column("CheckIn", width=100)
    admin_bookings_tree.column("CheckOut", width=100)
    admin_bookings_tree.column("Guests", width=80)
    admin_bookings_tree.column("Price", width=120)
    admin_bookings_tree.column("Status", width=150)
    
    admin_bookings_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_admin_bookings():
        admin_bookings_tree.delete(*admin_bookings_tree.get_children())
        data = load_data()
        all_bookings = get_all_bookings()
        
        for booking in all_bookings:
            hotel_name = next((h['name'] for h in data['hotels'] if h['id'] == booking['hotel_id']), "Неизвестно")
            total_price = booking['price'] * ((datetime.strptime(booking['check_out'], '%Y-%m-%d') - 
                                            datetime.strptime(booking['check_in'], '%Y-%m-%d')).days)
            
            admin_bookings_tree.insert('', 'end', values=(
                booking['booking_id'],
                hotel_name,
                booking['room_id'],
                booking['user_login'],
                booking['check_in'],
                booking['check_out'],
                booking['guests'],
                f"{total_price} руб.",
                booking['status']
            ))

    def approve_booking():
        selected = admin_bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите бронирование!")
            return
            
        booking_id = admin_bookings_tree.item(selected[0])['values'][0]
        current_status = admin_bookings_tree.item(selected[0])['values'][8]
        
        if current_status != 'на рассмотрении':
            messagebox.showwarning("Внимание", "Можно подтверждать только бронирования 'на рассмотрении'!")
            return
            
        if messagebox.askyesno("Подтверждение", f"Подтвердить бронирование #{booking_id}?"):
            if update_booking_status(booking_id, 'подтверждена'):
                messagebox.showinfo("Успех", "Бронирование подтверждено!")
                refresh_admin_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось подтвердить бронирование!")

    def cancel_booking_admin():
        selected = admin_bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите бронирование!")
            return
            
        booking_id = admin_bookings_tree.item(selected[0])['values'][0]
        current_status = admin_bookings_tree.item(selected[0])['values'][8]
        
        if current_status == 'отменена':
            messagebox.showwarning("Внимание", "Бронирование уже отменено!")
            return
            
        if messagebox.askyesno("Отмена бронирования", f"Отменить бронирование #{booking_id}?"):
            if update_booking_status(booking_id, 'отменена'):
                messagebox.showinfo("Успех", "Бронирование отменено!")
                refresh_admin_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось отменить бронирование!")

    bookings_control = tk.Frame(bookings_frame, bg=STYLES['bg_color'])
    bookings_control.pack(fill='x', padx=20, pady=10)

    create_button(bookings_control, "✅ Подтвердить", approve_booking, 'success').pack(side='left', padx=5)
    create_button(bookings_control, "❌ Отменить", cancel_booking_admin, 'danger').pack(side='left', padx=5)
    create_button(bookings_control, "🔄 Обновить", refresh_admin_bookings, 'default').pack(side='left', padx=5)

    # === ВКЛАДКА ЗАПРОСЫ НА ОТМЕНУ ===
    cancel_requests_tree = ttk.Treeview(cancel_requests_frame, 
                                      columns=("RequestID", "BookingID", "User", "Reason", "Created", "Status"), 
                                      show="headings")
    cancel_requests_tree.heading("RequestID", text="🔑 ID Запроса")
    cancel_requests_tree.heading("BookingID", text="📋 ID Брони")
    cancel_requests_tree.heading("User", text="👤 Пользователь")
    cancel_requests_tree.heading("Reason", text="📝 Причина")
    cancel_requests_tree.heading("Created", text="📅 Дата создания")
    cancel_requests_tree.heading("Status", text="📊 Статус")
    cancel_requests_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_cancel_requests():
        cancel_requests_tree.delete(*cancel_requests_tree.get_children())
        pending_requests = get_pending_cancel_requests()
        
        for request in pending_requests:
            cancel_requests_tree.insert('', 'end', values=(
                request['request_id'],
                request['booking_id'],
                request['user_login'],
                request.get('reason', 'Не указана'),
                request['created_at'],
                request['status']
            ))

    def approve_cancel_request():
        selected = cancel_requests_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запрос на отмену!")
            return
            
        request_id = cancel_requests_tree.item(selected[0])['values'][0]
        booking_id = cancel_requests_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Подтверждение отмены", 
                             f"Подтвердить отмену бронирования #{booking_id}?\n"
                             f"Запрос на отмену #{request_id}"):
            # Обновляем статус запроса
            if update_cancel_request_status(request_id, 'одобрено'):
                # Отменяем бронирование
                if update_booking_status(booking_id, 'отменена'):
                    messagebox.showinfo("Успех", "Запрос на отмену одобрен! Бронирование отменено.")
                    refresh_cancel_requests()
                    refresh_admin_bookings()
                else:
                    messagebox.showerror("Ошибка", "Не удалось отменить бронирование!")
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить статус запроса!")

    def reject_cancel_request():
        selected = cancel_requests_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запрос на отмену!")
            return
            
        request_id = cancel_requests_tree.item(selected[0])['values'][0]
        booking_id = cancel_requests_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Отклонение запроса", 
                             f"Отклонить запрос на отмену #{request_id}?\n"
                             f"Бронирование #{booking_id} останется активным."):
            # Обновляем статус запроса
            if update_cancel_request_status(request_id, 'отклонено'):
                messagebox.showinfo("Успех", "Запрос на отмену отклонен.")
                refresh_cancel_requests()
            else:
                messagebox.showerror("Ошибка", "Не удалось отклонить запрос!")

    cancel_requests_control = tk.Frame(cancel_requests_frame, bg=STYLES['bg_color'])
    cancel_requests_control.pack(fill='x', padx=20, pady=10)

    create_button(cancel_requests_control, "✅ Одобрить отмену", approve_cancel_request, 'success').pack(side='left', padx=5)
    create_button(cancel_requests_control, "❌ Отклонить запрос", reject_cancel_request, 'danger').pack(side='left', padx=5)
    create_button(cancel_requests_control, "🔄 Обновить", refresh_cancel_requests, 'default').pack(side='left', padx=5)

    # === ВКЛАДКА ПОЛЬЗОВАТЕЛИ ===
    users_tree = ttk.Treeview(users_frame, columns=("Login", "Role", "Hotel"), show="headings")
    users_tree.heading("Login", text="Логин")
    users_tree.heading("Role", text="Роль")
    users_tree.heading("Hotel", text="Гостиница")
    users_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_users():
        users_tree.delete(*users_tree.get_children())
        data = load_data()
        
        for user in data['users']:
            if user['login'] != 'admin':
                hotel_name = user.get('hotel_name', '') if user['role'] == 'hotel' else ''
                users_tree.insert('', 'end', values=(user['login'], user['role'], hotel_name))

    def delete_user():
        selected = users_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления!")
            return
            
        login, role, hotel = users_tree.item(selected[0])['values']
        
        if role == 'hotel':
            if messagebox.askyesno("Предупреждение", 
                                  f"Удаление пользователя гостиницы также удалит гостиницу '{hotel}' и все её номера. Продолжить?"):
                data = load_data()
                hotel_id = next((u.get('hotel_id') for u in data['users'] if u['login'] == login), None)
                if hotel_id:
                    data['hotels'] = [h for h in data['hotels'] if h['id'] != hotel_id]
                    data['rooms'] = [r for r in data['rooms'] if r['hotel_id'] != hotel_id]
        
        data['users'] = [u for u in data['users'] if u['login'] != login]
        save_data(data)
        messagebox.showinfo("Успех", f"Пользователь {login} удален!")
        refresh_users()

    users_control = tk.Frame(users_frame, bg=STYLES['bg_color'])
    users_control.pack(fill='x', padx=20, pady=10)

    create_button(users_control, "❌ Удалить пользователя", delete_user, 'danger').pack(side='left', padx=5)
    create_button(users_control, "🔄 Обновить", refresh_users, 'default').pack(side='left', padx=5)

    # Загружаем начальные данные
    refresh_hotels()
    refresh_admin_bookings()
    refresh_cancel_requests()
    refresh_users()
    center_window(win)

# ------------------- ОБНОВЛЕННАЯ РЕГИСТРАЦИЯ -------------------
def register_window(root):
    win = tk.Toplevel(root)
    win.title("Регистрация")
    win.geometry("450x350")
    win.configure(bg=STYLES['bg_color'])
    win.transient(root)
    win.grab_set()

    # Заголовок
    header_frame = tk.Frame(win, bg=STYLES['bg_color'])
    header_frame.pack(pady=20)
    
    create_header(header_frame, "Создание аккаунта", 18).pack()
    tk.Label(header_frame, text="Заполните все поля для регистрации", 
             font=('Arial', 10), bg=STYLES['bg_color'], fg=STYLES['text_light']).pack()

    # Форма
    form_frame = create_card(win, padx=30, pady=20)
    form_frame.pack(padx=20, pady=10, fill='both', expand=True)

    fields = [
        ("Логин:", "entry"),
        ("Пароль:", "entry_password"),
        ("Роль:", "combobox")
    ]

    entries = {}
    for i, (label_text, field_type) in enumerate(fields):
        row_frame = tk.Frame(form_frame, bg=STYLES['card_bg'])
        row_frame.grid(row=i, column=0, sticky='ew', pady=8)
        
        tk.Label(row_frame, text=label_text, font=('Arial', 10, 'bold'), 
                bg=STYLES['card_bg'], fg=STYLES['text_dark']).pack(side='left', padx=(0, 10))
        
        if field_type == "entry":
            entry = tk.Entry(row_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
            entry.pack(side='left', fill='x', expand=True)
            entries['login'] = entry
        elif field_type == "entry_password":
            entry = tk.Entry(row_frame, show='*', font=('Arial', 10), width=25, relief='solid', bd=1)
            entry.pack(side='left', fill='x', expand=True)
            entries['password'] = entry
        elif field_type == "combobox":
            combo = ttk.Combobox(row_frame, values=[ "client", "hotel"], 
                               font=('Arial', 10), width=23, state='readonly')
            combo.pack(side='left', fill='x', expand=True)
            entries['role'] = combo

    entries['login'].focus()

    def do_register():
        data = load_data()
        login = entries['login'].get().strip()
        password = entries['password'].get().strip()
        role = entries['role'].get().strip()

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

    # Кнопки
    button_frame = tk.Frame(win, bg=STYLES['bg_color'])
    button_frame.pack(pady=20)

    create_button(button_frame, "✅ Регистрация", do_register, 'success', width=15).pack(side='left', padx=10)
    create_button(button_frame, "🚪 Войти", lambda: [win.destroy(), login_window(root)], 'default', width=15).pack(side='left', padx=10)

    center_window(win)

# ------------------- ВХОД (БЕЗ ИЗМЕНЕНИЙ) -------------------
def login_window(root):
    win = tk.Toplevel(root)
    win.title("Вход в систему")
    win.geometry("450x350")
    win.configure(bg=STYLES['bg_color'])
    win.transient(root)
    win.grab_set()

    # Заголовок
    header_frame = tk.Frame(win, bg=STYLES['bg_color'])
    header_frame.pack(pady=30)
    
    create_header(header_frame, "Вход в систему", 20).pack()
    tk.Label(header_frame, text="Введите ваши учетные данные", 
             font=('Arial', 10), bg=STYLES['bg_color'], fg=STYLES['text_light']).pack()

    # Форма
    form_frame = create_card(win, padx=30, pady=25)
    form_frame.pack(padx=30, pady=10, fill='both', expand=True)

    tk.Label(form_frame, text="Логин:", font=('Arial', 10, 'bold'), 
            bg=STYLES['card_bg'], fg=STYLES['text_dark']).grid(row=0, column=0, sticky='w', pady=15)
    login_entry = tk.Entry(form_frame, font=('Arial', 10), width=25, relief='solid', bd=1)
    login_entry.grid(row=0, column=1, padx=10, pady=15, sticky='ew')
    login_entry.focus()

    tk.Label(form_frame, text="Пароль:", font=('Arial', 10, 'bold'), 
            bg=STYLES['card_bg'], fg=STYLES['text_dark']).grid(row=1, column=0, sticky='w', pady=15)
    pass_entry = tk.Entry(form_frame, show='*', font=('Arial', 10), width=25, relief='solid', bd=1)
    pass_entry.grid(row=1, column=1, padx=10, pady=15, sticky='ew')

    form_frame.columnconfigure(1, weight=1)

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

    # Кнопки
    button_frame = tk.Frame(win, bg=STYLES['bg_color'])
    button_frame.pack(pady=20)

    create_button(button_frame, "🚪 Войти", do_login, 'success', width=15).pack(side='left', padx=10)
    create_button(button_frame, "📝 Регистрация", lambda: [win.destroy(), register_window(root)], 'default', width=15).pack(side='left', padx=10)

    center_window(win)

# ------------------- ГЛАВНОЕ ОКНО (БЕЗ ИЗМЕНЕНИЙ) -------------------
def main():
    root = tk.Tk()
    root.title("Система бронирования турфирмы")
    root.geometry("600x500")
    root.configure(bg=STYLES['bg_color'])
    
    setup_styles()
    create_test_data()  # Создаем тестовые данные при запуске

    # Центрирование главного окна
    root.eval('tk::PlaceWindow . center')

    main_frame = tk.Frame(root, bg=STYLES['bg_color'])
    main_frame.pack(expand=True, fill='both', padx=50, pady=50)

    # Заголовок
    header_frame = tk.Frame(main_frame, bg=STYLES['bg_color'])
    header_frame.pack(pady=40)
    
    create_header(header_frame, "Система бронирования турфирмы", 22).pack()
    tk.Label(header_frame, text="Добро пожаловать в систему управления бронированиями", 
             font=('Arial', 12), bg=STYLES['bg_color'], fg=STYLES['text_light']).pack(pady=15)

    # Кнопки
    button_frame = tk.Frame(main_frame, bg=STYLES['bg_color'])
    button_frame.pack(pady=40)

    create_button(button_frame, "🚪 Вход в систему", lambda: login_window(root), 
                 'success', width=25, height=2, font_size=12).pack(pady=15)
              
    create_button(button_frame, "📝 Регистрация", lambda: register_window(root), 
                 'primary', width=25, height=2, font_size=12).pack(pady=15)

    # Статус базы данных
    data = load_data()
    bookings_data = load_bookings()
    status_frame = tk.Frame(main_frame, bg=STYLES['bg_color'])
    status_frame.pack(pady=20)
    
    status_text = f"📊 Статистика системы: 👥 Пользователей: {len(data['users'])} | 🏨 Гостиниц: {len(data['hotels'])} | 🛏️ Номеров: {len(data['rooms'])} | 📋 Броней: {len(bookings_data['bookings'])}"
    tk.Label(status_frame, text=status_text, font=('Arial', 10), 
             bg=STYLES['bg_color'], fg=STYLES['text_light']).pack()

    root.mainloop()

if __name__ == "__main__":
    main()