import pyautogui
from time import sleep
import sys
import threading
import keyboard

from PIL import ImageGrab, Image
from functools import partial
from Bungaa_utils import get_cords_cookie_clicker_window, find_on_screenshot, get_cords_main_cookie
# ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)




class Main_Programm():
    

    def start_main_cookie_clicker(self, main_cookie_filename, window_region, resize_step, my_confidence, main_cookie_min_scale):
        """
        Поиск координат главной печеньки
        Включение автокликера по главной печеньке
        Если была найдена точка появления золотой печенюхи, то включается ее сбор
        """
        
        # Поиск координат главной печеньки
        main_cookie_cords = get_cords_main_cookie(main_cookie_filename, window_region, resize_step, my_confidence, main_cookie_min_scale, exit_event, pause_bot_event, self.windows_os)
        
        while True:
            if not (exit_event.is_set() or pause_bot_event.is_set() or golden_cookie_event.is_set()):
                # Клик по основной печенюхе
                pyautogui.click(main_cookie_cords)
                
            # Если эвент поиска печенюхи включен, то кликаем по ней
            elif golden_cookie_event.is_set():
                pyautogui.click(self.golden_cookie_cords)
                # Чтобы не нажимать несколько раз по одной золотой печенюхе, делаем перерыв 0.5 сек
                sleep(0.5)
                # Отключение эвента по сбору золотой печенюхи
                golden_cookie_event.clear()
            # При выходе из программы, выходим из цикла
            elif exit_event.is_set():
                break
            # При выходе из паузы снова ищем МП окна и координаты главной печеньки
            elif pause_bot_event.is_set():
                # При выходе из паузы снова ищем МП окна и координаты главной печеньки на случай, если окно было передвинуто/изменен размер окна
                window_region = self.pause_bot()
                main_cookie_cords = main_cookie_cords = get_cords_main_cookie(main_cookie_filename, window_region, resize_step, my_confidence, main_cookie_min_scale, exit_event, pause_bot_event, self.windows_os)
            sleep(0.00001)


    def golden_cookie_searcher(self, golden_cookie_filename, window_region, resize_step, my_confidence, enable_search_logs):
        """
        Функция поиска золотых печенюх
        - Определяет, подан список картинок или одна картинка
        - Ведет подсчет попыток поиска и найденных золотых печенюх
        - Запускает функцию поиска по картинке
        """
        
        # Кол-во найденных печенюх
        gold_number = 0
        # Кол-во попыток поиска
        search_num = 1
        # Обработка случая, когда подается несколько картинок для поиска
        if type(golden_cookie_filename) == list:
            golden_img_var = []
            for filename in golden_cookie_filename:
                golden_img_var.append(Image.open(filename).convert('RGBA'))
        else:
            golden_img_var = Image.open(golden_cookie_filename).convert('RGBA')
        
        
        while True:
            if not (exit_event.is_set() or pause_bot_event.is_set()):
                # Вывод статистики
                if enable_search_logs:
                    print(f"Поиск золота... Попытка №{search_num}. Всего найдено печенюх: {gold_number}")
                # Запуск поиска золотого печенья на скриншоте игры
                self.golden_cookie_cords = find_on_screenshot(golden_img_var, window_region, resize_step, my_confidence, exit_event, pause_bot_event, self.windows_os)
                # + к статистике поиска
                search_num += 1
            
                # Если поиск успешный - запускаем эвент по нажатию
                if self.golden_cookie_cords:
                    # + к статистике золотых печенек
                    gold_number += 1
                    print(f"Золотая вкусняха №{gold_number}!")
                    # Активация эвента по сбору
                    golden_cookie_event.set()
                    # Чтобы не искать печеньку, пока не исчезнет старая
                    sleep(1)
                    
            # При выходе из программы
            elif exit_event.is_set():
                break
            # При паузе бота
            elif pause_bot_event.is_set():
                # Получаем новые координаты окна, на случай перемещения/изменения размеров окна
                window_region = self.pause_bot()
                # Откладываем запуск поиска золотых печенек, чтобы кликер по главной печеньке запустился
                sleep(1.5)
                
    
    def pause_bot(self):
        """
        Включет паузу для бота. Возвращает местоположение окна игры для случая перемещения окна/изменения размеров
        """
        
        while True:
            # При отключении паузы
            if not pause_bot_event.is_set():
                # Поиск нового пестоположения окна
                return get_cords_cookie_clicker_window(exit_event, pause_bot_event)
            elif exit_event.is_set():
                break
            sleep(0.5) 
            

    def interrupt_programm(self, clicker_thread):
        """
        Функция проверки нажатия кнопки выхода, завершения потока самой программы, включения паузы бота
        """
        
        while True:
            # Если нажата Q или главный поток остановил работы - выходим
            if keyboard.is_pressed('q') or not clicker_thread.is_alive():
                print("Выключение бота...")
                exit_event.set()
                sys.exit()
            # Если нажата P - приостанавливаем или продолжаем работу программы
            elif keyboard.is_pressed('p'):
                # Если пауза не стоит, включаем паузу
                if not pause_bot_event.is_set():
                    pause_bot_event.set()
                    print("~~~Пауза~~~")
                    # Для исключения включения и выключения одним нажатием
                    sleep(1)
                # Если пауза стоит, выключаем паузу
                else:
                    pause_bot_event.clear()
                    print("~~~Запуск~~~")
                    # Для исключения включения и выключения одним нажатием
                    sleep(1)
            sleep(0.05)
        
            
    def start_programm(self):
        """
        Запуск основной программы
        0) Основные параметры для поиска изображений
        1) Поиск координат окна игры
        3) Запуск треда по поиску золотой печеньки
        4) Включение автокликера на по основной печеньке
        """
        
        # Название файла главной печеньки для поиска
        main_cookie_filename = "perfectCookie_cropped.png"
        # Название файлов для поиска золотой печеньки
        # Эксперименты показали, что лучше всего ищутся изображения с шагом поворота в 8* 
        golden_cookie_filename = ["goldCookie_cropped.png", "goldCookie_cropped_8.png", "goldCookie_cropped_16.png", "goldCookie_cropped_352.png", "goldCookie_cropped_344.png"]
        # Шаг для проверки масшатибруемых изображений
        resize_step = 0.05
        # Нижний порог зума для поиска главной печеньки
        main_cookie_min_scale = 0.3
        # Насколько похожа печенька на оригинал (0.1 - 1)
        # Эксперименты показали, что 0.5 оптимальное значение для поиска золотой печеньки. 
        my_confidence = 0.5
        # Включить вывод логов на каждую попытку поиска золотой печеньки
        enable_search_logs = True
        # На windows возможно включить поддержку нескольких мониторов, в другом случае будет работать только на основном мониторе
        self.windows_os = True
        
        
        
        # Поиск местоположения окна cookie_clicker
        window_region = get_cords_cookie_clicker_window(exit_event, pause_bot_event)
        
        # Поток для запуска кликера
        clicker_thread = threading.Thread(target=self.start_main_cookie_clicker, args=(main_cookie_filename, window_region, resize_step, my_confidence, main_cookie_min_scale))
        clicker_thread.start()
        
        # Поток для ожидания нажатий выхода/паузы программы
        interrup_thread = threading.Thread(target=lambda: self.interrupt_programm(clicker_thread))
        interrup_thread.start()
        
        sleep(1)
        # Поток для поиска золотой печеньки
        golden_thread = threading.Thread(target=self.golden_cookie_searcher, args=(golden_cookie_filename, window_region, resize_step, my_confidence, enable_search_logs))
        golden_thread.start()
        
def get_event_status(event_name):
    """
    Функция для передачи статуса эвента в utils
    """
    if event_name == "exit":
        return exit_event.is_set()
    elif event_name == "pause":
        return pause_bot_event.is_set()

if __name__ == "__main__":
    
    # Эвент выхода из программы
    exit_event = threading.Event()
    # Эвент клика по золотой печеньке
    golden_cookie_event = threading.Event()
    # Эвент паузы бота
    pause_bot_event = threading.Event()
    
    # Запуск программы
    main_class = Main_Programm()
    main_class.start_programm()
    
