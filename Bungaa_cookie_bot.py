from time import sleep
import sys
import threading
import keyboard
from Bungaa_utils import    feature_matching, get_cords_main_cookie, background_click, \
                            get_cookie_window, path_var_to_list, disable_background_freeze_setting



class Main_Programm():
    

    def start_main_cookie_clicker(self, main_cookie_image_list, my_confidence):
        """
        Поиск координат главной печеньки
        Включение автокликера по главной печеньке
        Если была найдена точка появления золотой печенюхи, то включается ее сбор
        """
        
        # Поиск координат главной печеньки
        main_cookie_cords = get_cords_main_cookie(self.cookie_window, main_cookie_image_list, my_confidence, pause_bot_event)
        
        while True:
            
            if not (exit_event.is_set() or pause_bot_event.is_set() or golden_cookie_event.is_set()):
                # Клик по основной печенюхе
                # pyautogui.click(main_cookie_cords)
                background_click(self.cookie_window, main_cookie_cords[0], main_cookie_cords[1])
                
                
            # Если эвент поиска печенюхи включен, то кликаем по ней
            elif golden_cookie_event.is_set():
                
                # Клик по печеньке
                background_click(self.cookie_window, self.golden_cookie_cords[0], self.golden_cookie_cords[1])
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
                self.pause_bot()
                main_cookie_cords = get_cords_main_cookie(self.cookie_window, main_cookie_image_list, my_confidence, pause_bot_event)
                if main_cookie_cords:
                    main_cookie_cords_x, main_cookie_cords_y = main_cookie_cords
                    
            sleep(0.00001)


    def click_event_searcher(self, click_event_image_list, my_confidence, enable_search_logs):
        """
        Функция поиска золотых печенюх
        - Определяет, подан список картинок или одна картинка
        - Ведет подсчет попыток поиска и найденных золотых печенюх
        - Запускает функцию поиска по картинке
        """
        
        # Кол-во найденных печенюх
        click_number = 0
        # Кол-во попыток поиска
        search_num = 1
        
        while True:
            if not (exit_event.is_set() or pause_bot_event.is_set()):
                # Вывод статистики
                if enable_search_logs:
                    print(f"Поиск кликательных вещей... Попытка №{search_num}. Всего найдено: {click_number}")
                    # + к статистике поиска
                    search_num += 1
                    
                # Запуск поиска золотого печенья на скриншоте игры
                self.golden_cookie_cords = feature_matching(self.cookie_window, click_event_image_list, my_confidence)
                
                # Если поиск успешный - запускаем эвент по нажатию
                if self.golden_cookie_cords:
                    # + к статистике золотых печенек
                    click_number += 1
                    print(f"Нашли нажимашку №{click_number}!")
                    # Активация эвента по сбору
                    golden_cookie_event.set()
                    # Чтобы не искать печеньку, пока не исчезнет старая
                    sleep(1.5)
                    
            # При выходе из программы
            elif exit_event.is_set():
                break
            # При паузе бота
            elif pause_bot_event.is_set():
                # Функция паузы
                self.pause_bot()
                # Откладываем запуск поиска золотых печенек, чтобы кликер по главной печеньке запустился
                sleep(1)
                
            sleep(2)
                
    
    def pause_bot(self):
        """
        Включет паузу для бота. Возвращает местоположение окна игры для случая перемещения окна/изменения размеров
        """
        
        while True:
            # При отключении паузы или выходе
            if not pause_bot_event.is_set() or exit_event.is_set():
                # На случай перезапуска игры по время паузы еще раз ищем окно
                self.cookie_window = get_cookie_window()
                break
            sleep(0.5) 
            

    def interrupt_programm(self, clicker_thread, pause_button, quit_button):
        """
        Функция проверки нажатия кнопки выхода, завершения потока самой программы, включения паузы бота
        """
        
        while True:
            # Если нажата Q или главный поток остановил работы - выходим
            if keyboard.is_pressed(quit_button) or not clicker_thread.is_alive():
                print("Выключение бота...")
                exit_event.set()
                sys.exit()
            # Если нажата P - приостанавливаем или продолжаем работу программы
            elif keyboard.is_pressed(pause_button):
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
        0) Параметры настроек
        1) Выключение фриза анимаций при окне в бэкграунде
        2) Конвертирование путей к искомым картинкам в формат list
        3) Получение окна игры с помощью win32
        4) Включение основного кликера
        5) Включение функции для паузы/завершения скрипта
        6) Включение поиска золотой печеньки
        """
        # Кнопка паузы
        pause_button = "ctrl+p"
        # Кнопка выхода
        quit_button = "ctrl+q"
        # Название файла главной печеньки для поиска
        main_cookie_image_path = "perfectCookie.png"
        # Название файлов для поиска золотой печеньки
        event_image_path = ["goldCookie.png", "frostedReindeer.png"]
        # Значение для feature matching отбора. Означает точность совпадения. (меньшее значение = более точное совпадение)
        my_confidence = 120
        # Включить вывод логов на каждую попытку поиска золотой печеньки и etc
        enable_search_logs = True
        
        # При True скрипт проверяет, включена ли настройка полного фриза анимаций игры,
        # когда окно полностью прикрыто другим окном
        disable_background_animation_freeze = True
        # Путь к папке с игрой
        game_folder_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Cookie Clicker"
        
        
        # Отключение полного фриза анимаций
        if disable_background_animation_freeze:
            disable_background_freeze_setting(game_folder_path)
        
        # Если путь к искомым объектам задан строчкой, то он преобразовывается в список (для дальнейшего удобства)
        main_cookie_image_path = path_var_to_list(main_cookie_image_path)
        event_image_path = path_var_to_list(event_image_path)
        
        # Поиск окна cookie_clicker
        self.cookie_window = get_cookie_window()
        
        # Поток для запуска кликера
        clicker_thread = threading.Thread(target=self.start_main_cookie_clicker, args=(main_cookie_image_path, my_confidence))
        clicker_thread.start()
        
        # Поток для ожидания нажатий выхода/паузы программы
        interrup_thread = threading.Thread(target=lambda: self.interrupt_programm(clicker_thread, pause_button, quit_button))
        interrup_thread.start()
        
        sleep(1)
        # Поток для поиска золотой печеньки
        golden_thread = threading.Thread(target=self.click_event_searcher, args=(event_image_path, my_confidence, enable_search_logs))
        golden_thread.start()
        
        

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
    
