import pyautogui
from time import sleep
import sys
import threading
import keyboard

from PIL import ImageGrab, Image
from functools import partial
# ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

# print(pyautogui.size())
#Point(x=1089, y=640)

# while True:
#     print(pyautogui.position())
#     sleep(0.5)

class Main_Programm(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)


    def get_cords_golden_cookie_window(self):
        """
        Получает координаты окна cookie clicker
        При неудаче будет делать попытки каждую секундуPoint(x=1493, y=643)
        """
        while True:
            window_cords = pyautogui.getWindowsWithTitle("Cookie Clicker")
            if window_cords == []:
                print("Окно не найдено. Следующая попытка через секунду.")
                if exit_event.is_set():
                    break
                sleep(1)
                continue
            return window_cords[0].left, window_cords[0].top, window_cords[0].width, window_cords[0].height
        
    
    def find_rotated_image(self, img, window_region, resize_step, max_angle, angle_step, my_confidence):
        """
        Поворачивает и приближает изображение
        для удаления черных полей после поворота
        """
        
        angles = list(range(360 - max_angle, 360, angle_step)) + list(range(0, max_angle + 1, angle_step))
        for angle in angles:
            if exit_event.is_set():
                break
            # border_percent = 0.08
            # border = border_percent * img.size[0]
            rotated_img = img.rotate(angle)#.crop((border, border, img.size[0] - border, img.size[1] - border))
                
            # img.save(f'modified_{main_cookie_filename}')
            # img_center_cords = pyautogui.locateCenterOnScreen(f'modified_{main_cookie_filename}' , grayscale=True, confidence = my_confidence, region=window_region)
            img_center_cords = self.find_resized_image(rotated_img, window_region, resize_step, my_confidence, is_golden = True)
            if img_center_cords: return img_center_cords
        
        
    def find_resized_image(self, orig_image, window_region, resize_step, my_confidence, min_scale = 0.6, is_golden = False):
        
        scale_range = [scale / 100 for scale in range(100, round(min_scale * 100 - 1), round(-resize_step * 100))]
        orig_image_side_size = orig_image.size[0]
        
        for scale in scale_range:
            if exit_event.is_set():
                break
            modded_img = orig_image.copy()
            size = orig_image_side_size * scale, orig_image_side_size * scale
            modded_img.thumbnail(size, Image.Resampling.LANCZOS)
            # if not is_golden:
            #     modded_img.show()

            img_center_cords = pyautogui.locateCenterOnScreen(modded_img, confidence = my_confidence, region=window_region)
            
            if img_center_cords: return img_center_cords
            
    def find_rotated_image_on_screenshot(self, orig_image, window_region, resize_step, max_angle, angle_step, my_confidence):
        """
        Поворачивает и приближает изображение
        для удаления черных полей после поворота
        """
        screenshot_image = pyautogui.screenshot(region = window_region)
        angles = list(range(360 - max_angle, 360, angle_step)) + list(range(0, max_angle + 1, angle_step))
        for angle in angles:
            if exit_event.is_set():
                break
            # border_percent = 0.08
            # border = border_percent * img.size[0]
            rotated_img = orig_image.rotate(angle)#.crop((border, border, img.size[0] - border, img.size[1] - border))
                
            # img.save(f'modified_{main_cookie_filename}')
            # img_center_cords = pyautogui.locateCenterOnScreen(f'modified_{main_cookie_filename}' , grayscale=True, confidence = my_confidence, region=window_region)
            img_center_cords = self.find_on_screenshot(rotated_img, window_region, resize_step, my_confidence, screenshot_image=screenshot_image)
            if img_center_cords: return img_center_cords
            
    def find_on_screenshot(self, orig_image, window_region, resize_step, my_confidence, min_scale = 0.6, screenshot_image = None):
        
        def find_with_scaling(orig_image, orig_image_side_size, scale_range, screenshot_image, my_confidence, window_region):
            for scale in scale_range:
                if exit_event.is_set():
                    break
                modded_img = orig_image.copy()
                size = orig_image_side_size * scale, orig_image_side_size * scale
                modded_img.thumbnail(size, Image.Resampling.LANCZOS)
                # if not is_golden:LANCZOS
                #     modded_img.show()

                img_cords = pyautogui.locate(modded_img, screenshot_image, confidence = my_confidence)
                
                if img_cords: 
                    img_center_cords = pyautogui.center(img_cords)
                    img_center_cords_window = (img_center_cords.x + window_region[0], img_center_cords.y + window_region[1])
                    print(img_center_cords_window)
                    return img_center_cords_window
        
        scale_range = [scale / 100 for scale in range(120, round(min_scale * 100 - 1), round(-resize_step * 100))]
        if type(orig_image) == list:
            orig_image_side_size = orig_image[0].size[0]
        else: 
            orig_image_side_size = orig_image.size[0]
        
        if not screenshot_image:
            screenshot_image = pyautogui.screenshot(region = window_region)
        
        if type(orig_image) == list:
            for golden_img in orig_image:
                img_cords = find_with_scaling(golden_img, orig_image_side_size, scale_range, screenshot_image, my_confidence, window_region)
                if img_cords:
                    return img_cords
        else:
            img_cords = find_with_scaling(orig_image, orig_image_side_size, scale_range, screenshot_image, my_confidence, window_region)
            return img_cords
        

        
        
    def get_cords_main_cookie(self, main_cookie_filename, window_region, resize_step, my_confidence, min_scale):
        
        main_cookie_img = Image.open(main_cookie_filename).convert('RGBA')
        
        # main_cookie_cords = pyautogui.locateCenterOnScreen(main_cookie_filename , grayscale=True, confidence = my_confidence, region=window_region)
        # if main_cookie_cords == None:
            
        main_cookie_cords = self.find_resized_image(main_cookie_img, window_region, resize_step, my_confidence, min_scale=min_scale)
            
        if main_cookie_cords == None:
            print("Главная печенька не найдена")
            sys.exit()

        return main_cookie_cords


    def start_main_cookie_clicker(self, main_cookie_cords):
        while True:
            pyautogui.click(main_cookie_cords)
            if golden_cookie_event.is_set():
                pyautogui.click(self.golden_cookie_cords)
                sleep(0.5)
                golden_cookie_event.clear()
            # sleep(0.001)
            if exit_event.is_set():
                break
    
    def golden_cookie_searcher(self, golden_cookie_filename, window_region, resize_step, max_angle, angle_step, my_confidence):
        gold_number = 0
        if type(golden_cookie_filename) == list:
            golden_img_var = []
            for filename in golden_cookie_filename:
                golden_img_var.append(Image.open(filename).convert('RGBA'))
        else:
            golden_img_var = Image.open(golden_cookie_filename).convert('RGBA')
            
        search_num = 0
        while True:
            print(f"Поиск золота... {search_num}, найдено золота {gold_number}")
            # self.golden_cookie_cords = self.find_resized_image(golden_cookie_img, window_region, resize_step, my_confidence)
            self.golden_cookie_cords = self.find_on_screenshot(golden_img_var, window_region, resize_step, my_confidence)
            # self.golden_cookie_cords = self.find_rotated_image(golden_cookie_img, window_region, resize_step, max_angle, angle_step, my_confidence)
            # self.golden_cookie_cords = self.find_rotated_image_on_screenshot(golden_cookie_img, window_region, resize_step, max_angle, angle_step, my_confidence)
            if self.golden_cookie_cords != None:
                gold_number += 1
                print(f"Золотая вкусняха №{gold_number}!")
                golden_cookie_event.set()
                # Чтобы не кликать второй раз по исчезающец печеньке
                sleep(1)
            search_num += 1
            if exit_event.is_set():
                break
        
            
    def run(self):
        
        # main_cookie_filename = "perfectCookie.png"
        main_cookie_filename = "perfectCookie_cropped.png"
        # golden_cookie_filename = "golden_cookie.jpg"
        # golden_cookie_filename = "goldCookie.png"
        # golden_cookie_filename = "goldCookie_cropped.png"
        golden_cookie_filename = ["goldCookie_cropped.png", "goldCookie_cropped_8.png", "goldCookie_cropped_16.png", "goldCookie_cropped_352.png", "goldCookie_cropped_344.png"]
        # Шаг для проверки масшатибруемых изображений
        resize_step = 0.05
        main_cookie_min_scale = 0.3
        # Рендж поворота золотой печеньки
        max_angle_golden = 12
        # Шаг проверки поворота золотой печеньки
        angle_step_golden = 1
        #Насколько похожа печенька на оригинал (0.1 - 1)
        my_confidence = 0.5
        
        # Поиск координат окна cookie_clicker
        window_region = self.get_cords_golden_cookie_window()
        main_cookie_cords = self.get_cords_main_cookie(main_cookie_filename, window_region, resize_step, my_confidence, main_cookie_min_scale)
        
        # Поиск золотой печеньки
        golden_thread = threading.Thread(target=self.golden_cookie_searcher, args=(golden_cookie_filename, window_region, resize_step, max_angle_golden, angle_step_golden, my_confidence))
        golden_thread.start()
        
        self.start_main_cookie_clicker(main_cookie_cords)
        

def check_for_golden_cookie():
    pass

def interrupt_programm():
    while True:
        if keyboard.is_pressed('q') or not main_thread.is_alive():
            exit_event.set()
            sys.exit()
        sleep(0.1)

if __name__ == "__main__":
    exit_event = threading.Event()
    golden_cookie_event = threading.Event()
    
    main_thread = Main_Programm()
    main_thread.start()
    interrupt_programm()





    # click_time = 0.1
    # my_confidence = 0.7   # точность совпадения, 70 %
    # my_region=(x_position,y_position, heigth, length) # Примерные координаты и размер окна игры. чем точнее координаты, тем быстрее поиск
    # internet_disconnect_button = pyautogui.locateCenterOnScreen('Pictures/internet_disconnect.png', confidence = my_confidence , grayscale=True, region=my_region) 

# if (internet_disconnect_button != None): 
#         pyautogui.moveTo(internet_disconnect_button[0],internet_disconnect_button[1], duration=click_time)
#         pyautogui.PAUSE = 2
#         pyautogui.click()