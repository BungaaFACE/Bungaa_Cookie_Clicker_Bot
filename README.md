# Bungaa_Cookie_Clicker_Bot
Бот для Desktop версии Cookie Clicker  

# Описание
Бот автоматически кликает на основную печеньку + собирает золотые печеньки при их появлении.  
Возможность установки паузы. Во время паузы можно передвигать окно, изменять размер - при выключении паузы программа заново все обнаружит.  

# Настройки
В боте есть следующие настройки:  
  Название файла главной печеньки для поиска:  
  `main_cookie_filename = "perfectCookie_cropped.png"`  
    
  Название файлов для поиска золотой печеньки:  
  `golden_cookie_filename = ["goldCookie_cropped.png", "goldCookie_cropped_8.png", "goldCookie_cropped_16.png", "goldCookie_cropped_352.png", "goldCookie_cropped_344.png"]`  
  Эксперименты показали, что лучше всего ищутся изображения с шагом поворота в 8 градусов и вплоть до 16  
    
  Шаг для проверки масшатибруемых изображений:  
  `resize_step = 0.05`  
    
  Нижний порог зума для поиска главной печеньки:  
  `main_cookie_min_scale = 0.3`  
    
  Насколько похожа печенька на оригинал (0.1 - 1):  
  `my_confidence = 0.5`  
  Эксперименты показали, что 0.5 оптимальное значение для поиска золотой печеньки.  
    
  Включить вывод логов на каждую попытку поиска золотой печеньки:  
  `enable_search_logs = True`  
    
  На windows возможно включить поддержку нескольких мониторов, в другом случае будет работать только на основном мониторе:  
  `self.windows_os = True`  

# Требования
Для работы нужно установить модули:
  - pyautogui  
  - keyboard  
  - PIL
  - cv2
  Команда для установки:
  `pip install opencv-python PyAutoGUI keyboard Pillow`

# Проблемы и особенности
Бот собирает 95% печенек, некоторые он не обнаруживает из-за специфики их появления (поворот под разным градусом, с разным размером, меняющаяся прозрачность и размеры).  
При уменьшении размера окна выполняется больше попыток обнаружения печеник в промежуток времени, благодаря меньшему региону поиска, что уменьшает кол-во пропущенных печенек.  

# Управление
  - Запустить Bungaa_cookie_bot.py  
  - Клавиша `"Q"` - выход из программы  
  - Клавиша `"P"` - включение паузы. Повторное нажатие - выключение паузы.  

