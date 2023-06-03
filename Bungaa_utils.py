import pyautogui
from PIL import Image, ImageGrab
from time import sleep
import sys


def get_cords_cookie_clicker_window(exit_event, pause_bot_event):
    """
    Получает координаты окна cookie clicker
    При неудаче будет делать попытки каждую секунду
    """
    while True:
        
        # Поиск окна с "Cookie Clicker" в названии
        window_cords = pyautogui.getWindowsWithTitle("Cookie Clicker")
        
        if window_cords == []:
            print("Окно не найдено. Следующая попытка через секунду.")
            
            # Если кнопка выхода или паузы была нажата, обрываем цикл
            if exit_event.is_set() or pause_bot_event.is_set():
                break
            
            sleep(1)
            continue
        
        # возвращаем начальные координаты (левый верхний угол) и ширину с высотой
        return window_cords[0].left, window_cords[0].top, window_cords[0].width, window_cords[0].height


def find_with_scaling(orig_image, orig_image_side_size, scale_range, screenshot_image, my_confidence, window_region, exit_event, pause_bot_event):
    """
    Поиск изображения под разным зумом изображения
    Рендж зумов подается в аргкментах
    """
    # Перебор разных значений зума
    for scale in scale_range:
        
        # Остановка поиска при выходе из программы или паузе
        if exit_event.is_set() or pause_bot_event.is_set():
            break
        
        # Копируем исходное изображение, поскольку метод thumbnail изменяет переменную, а не создает новую
        modded_img = orig_image.copy()
        # Вычисление ширины картинки при зуме
        size = orig_image_side_size * scale, orig_image_side_size * scale
        # Зум картинки; Resampling.LANCZOS лучше всего сжимает/расширяет картинку
        modded_img.thumbnail(size, Image.Resampling.LANCZOS)
        # Поиск картинки на скриншоте
        img_cords = pyautogui.locate(modded_img, screenshot_image, confidence = my_confidence)
        
        # Если изобрание != None (нашлось), то сразу отдаем результат
        if img_cords: 
            # Находим средние координаты изображения
            img_center_cords = pyautogui.center(img_cords)
            # Поскольку поиск был по скриншоту окошка игры, начальная точка рассчитана от начала окна (не всего экрана)
            # Поэтому плюсуем смещение начальной точки окна к уже полученным данным
            img_center_cords_window = (img_center_cords.x + window_region[0], img_center_cords.y + window_region[1])
            return img_center_cords_window


def find_on_screenshot(orig_image_var, window_region, resize_step, my_confidence, exit_event, pause_bot_event, windows_os, min_scale = 0.6, screenshot_image = None):
    """
    Функция подготавливает исходные данные для поиска
    - Подготавливает список множителей зума для проверки (0-1)
    - Берет длину стороны искомого изображения
    - Делает скриншот, если его не подали в начальных данных
    - Определяет orig_image_var list или одно изображение
    - Вызывает функцию поиска
    """
    # Рендж множителя зума картинки для поиска
    scale_range = [scale / 100 for scale in range(120, round(min_scale * 100 - 1), round(-resize_step * 100))]
    # Картинка - квадрат, поэтому выделяется одна сторона для подсчета длины при зуме картинки
    if type(orig_image_var) == list:
        orig_image_side_size = orig_image_var[0].size[0]
    else: 
        orig_image_side_size = orig_image_var.size[0]
    
    # Если на вход не подали изображение, на котором искать, делается скриншот окна
    if not screenshot_image:
        if windows_os:
            bbox_window = (window_region[0], window_region[1], window_region[0] + window_region[2], window_region[1] + window_region[3])
            screenshot_image = ImageGrab.grab(bbox=bbox_window, all_screens=True)
        else:
            screenshot_image = pyautogui.screenshot(region = window_region)
    # Если искомых изображений несколько, то перебираются все
    if type(orig_image_var) == list:
        for golden_img in orig_image_var:
            img_cords = find_with_scaling(golden_img, orig_image_side_size, scale_range, screenshot_image, my_confidence, window_region, exit_event, pause_bot_event)
            # Если изображение нашлось, то нет смысла перебирать остальные, возвращаем ответ
            if img_cords:
                return img_cords
    else:
        img_cords = find_with_scaling(orig_image_var, orig_image_side_size, scale_range, screenshot_image, my_confidence, window_region, exit_event, pause_bot_event)
        return img_cords
    

    
    
def get_cords_main_cookie(main_cookie_filename, window_region, resize_step, my_confidence, min_scale, exit_event, pause_bot_event, windows_os):
    """
    Функция открывает изображение главной печенюхи и вызывает функцию поиска по скриншоту
    """
    
    main_cookie_img = Image.open(main_cookie_filename).convert('RGBA')
    main_cookie_cords = find_on_screenshot(main_cookie_img, window_region, resize_step, my_confidence, exit_event, pause_bot_event, windows_os, min_scale=min_scale)
        
    if main_cookie_cords == None and not pause_bot_event.is_set():
        print("Главная печенька не найдена")
        # Остановка остальных потоков
        exit_event.set()
        # Выход
        sys.exit()
    elif pause_bot_event.is_set():
        return
            
    return main_cookie_cords