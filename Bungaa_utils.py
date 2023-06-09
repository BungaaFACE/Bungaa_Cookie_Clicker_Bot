from sys import exit
import win32.win32api as win32api
import win32.win32gui as win32gui
import win32.lib.win32con as win32con
import pythonwin.win32ui as win32ui
from ctypes import windll
import numpy as np
import cv2


def path_var_to_list(path):
    """
    При подаче string функция конвертирует переменную в list
    """
    if type(path) == str:
        path = [path]
    return path


def disable_background_freeze_setting(path):
    """
    Функция для отключения фриза анимаций при скрытии окна игры за другими окнами.
    """
    # Проверка слэша в конце пути
    if "Cookie Clicker\\" not in path:
        path = path + "\\"
        
    # Открытие конфига
    with open(f"{path}resources\\app\\start.js") as config:
        full_config = config.read()
    
    # Проверка параметра в конфигурации
    if "backgroundThrottling: false," not in full_config:
        
        # Поиск индекса, после которого нужно добавить параметр
        index = full_config.index("s:{") + 3
        # Добавление параметра
        full_config = full_config[:index] + "\n\t\t\tbackgroundThrottling: false," + full_config[index:]
        
        # Запись конфига с параметром обратно в файл и вывод сообщение о перезапуске игры
        with open(f"{path}resources\\app\\start.js", "w") as config:
            config.write(full_config)
        print("\nОтключена остановка анимации игры когда окно полностью прикрыто другим окном.")
        print("Это требуется для корректного поиска золотых печенек и т.п. в фоне.")
        print("Требуется перезагрузка игры.\n")
        exit()
        


def get_cookie_window():
    """
    Функция для получения окна
    Окно необходимо для дальнейшей работы с ним
    """
    
    def handle_windows(hwnd, useless_param):
        """
        Функция для нахождения нужного окна из списка всех окон
        """
        if "cookies - Cookie Clicker" in win32gui.GetWindowText(hwnd):
            cookie_window.append(hwnd)
            
    # Вывод окна в лист, чтобы вытащить его из функции без return
    cookie_window = []
    
    # Перебор всех окон и вызов функции handle_windows для каждого
    win32gui.EnumWindows(handle_windows, None)
    
    if cookie_window == []:
        print("Окно не найдено")
        exit()
        
    return cookie_window[0]


def get_window_region(hwnd):
    """
    Функция достает координаты и размеры окна
    """
    x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
    width = x1 - x0
    height = y1 - y0
    return (x0, y0, width, height)


def get_background_sreenshot(hwnd):
    """
    Функция делаем скриншот окна из фонового режима
    """
    
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    window_region = get_window_region(hwnd)
    width, height = window_region[2], window_region[3]
   
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)    
    saveDC.SelectObject(saveBitMap)
    
    # Printwindow нужно для избежания черного скриншота
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    
    bmpstr = saveBitMap.GetBitmapBits(True)
    
    # Конвертируем в матрицу для дальнейшего использования в CV2
    screenshot = np.frombuffer(bmpstr, dtype='uint8')
    screenshot.shape = (height, width, 4)
    
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return screenshot


def background_click(cookie_window, x, y):
    """
    Имитирует нажатия в окне без использования основного курсора (даже в окне на фоне)
    """
    
    lParam = win32api.MAKELONG(x, y)
    win32gui.SendMessage(cookie_window, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.SendMessage(cookie_window, win32con.WM_LBUTTONUP, None, lParam)
    
    
def feature_matching(cookie_window, image_list, my_confidence):
    """
    Поиск картинки совпадений картинок при помощи feature matching
    """
    
    # Делаем скриншот
    screenshot_image = get_background_sreenshot(cookie_window)
    # Фильтр для создания точек интереса картинки
    sift = cv2.SIFT_create()
    # Нахождение точек интереса картинки
    kp1, des1 = sift.detectAndCompute(screenshot_image, None)
    
    for golden_image_path in image_list:
        
        # Открываем искомую картинку
        golden_cookie_image = cv2.imread(golden_image_path, cv2.IMREAD_GRAYSCALE)
        # Нахождение точек интереса картинки
        kp2, des2 = sift.detectAndCompute(golden_cookie_image, None)

        # Ищем общие совпадения точек интереса обеих картинок
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(des1, des2)

        # Сортировка по лучшим совпадениям + обрезаем только до 10 лучших совпадений
        matches = sorted(matches, key=lambda x: x.distance)[:10]

        # Проверяем самый близкий матч, если по условию проходит, то продолжаем обработку
        if matches[0].distance < my_confidence:
            
            # Листы для поиска средней координаты
            coordinates_x_list, coordinates_y_list = [], []
            
            # Перебор точек интересна по уровню совпадения
            for match in matches:
                if match.distance < my_confidence:
                    coordinates_x_list.append((kp1[match.queryIdx].pt)[0])
                    coordinates_y_list.append((kp1[match.queryIdx].pt)[1])
                    
            # Находим среднее значение координат
            coordinates = (int(sum(coordinates_x_list) // len(coordinates_x_list)), int(sum(coordinates_y_list) // len(coordinates_y_list)))
            
            return coordinates
    
    
def get_cords_main_cookie(cookie_window, main_cookie_path, my_confidence, pause_bot_event):
    """
    Функция открывает изображение главной печенюхи и вызывает функцию поиска по скриншоту
    """
    
    # Запуск функции поиска по картинке
    main_cookie_cords = feature_matching(cookie_window, main_cookie_path, my_confidence)
    
    # Если игра не найдена, то включаем паузу
    if main_cookie_cords == None and not pause_bot_event.is_set():
        print("Главная печенька не найдена. Включение паузы")
        # Остановка остальных потоков
        pause_bot_event.set()
    elif pause_bot_event.is_set():
        return
            
    return main_cookie_cords