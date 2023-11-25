import asyncio
import datetime
from datetime import datetime
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import PIL
import pytesseract
import cv2
import numpy as np
import random

import adb
from adb import capture_screenshot #convert_coordinates
from adb import lock
from adb import tap_random
from adb import swipe

previous_file = '1.png'
current_file = '2.png'
crop_coords2 = (585, 329, 614, 357) #masslock
crop_coords = (1, 415, 185, 450) #local emulator
first_module = (650, 497)

def crop_image(image_path, crop_coords):
    img = cv2.imread(image_path)
    img_cropped = img[crop_coords[1]:crop_coords[3], crop_coords[0]:crop_coords[2]]
    return img_cropped

def process_image(file_path):
    img_cropped = crop_image(file_path, crop_coords)
    gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

async def processlock():
    image = cv2.imread("screenshot.png")
    img_cropped = image[crop_coords2[1]:crop_coords2[3], crop_coords2[0]:crop_coords2[2]]
    grayscale_image = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(grayscale_image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    processed_image = np.zeros_like(binary_image)
    cv2.drawContours(processed_image, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
    cv2.imwrite("lock.png", processed_image)
    total_pixels = processed_image.shape[0] * processed_image.shape[1]
    white_pixels = np.sum(processed_image == 255)
    white_pixels_percentage = (white_pixels / total_pixels) * 100
    if white_pixels_percentage >= 30:
        await lock()

async def find(keywords: str):
    capture_screenshot()
    await asyncio.sleep(1)
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    inverted_img = cv2.bitwise_not(img)
    x1, y1, x2, y2 = 728, 4, 912, 90
    cv2.rectangle(inverted_img, (x1, y1), (x2, y2), (0, 0, 0), -1)
    text_data = pytesseract.image_to_data(inverted_img, output_type='dict')
    keywords_list = keywords.lower().split(',')
    matching_words = []
    for i, word_text in enumerate(text_data['text']):
        if word_text.lower() in keywords_list:
            matching_words.append((i, word_text))
    if matching_words:
        i, word_text = random.choice(matching_words)
        x = text_data['left'][i]
        y = text_data['top'][i]
        w = text_data['width'][i]
        h = text_data['height'][i]
        click_x = x + w // 2
        click_y = y + h // 2
        click = (click_x, click_y)
        tap_random(click)
        return True
        print(matching_words)
        print(click)
    else:
        print("не найдены")
    cv2.imwrite("tess.png", inverted_img)

async def check_assist(): #проверка на наличие пикселя щита у первой залоченной неписи
    capture_screenshot()
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 929  # Координата x
    y = 56  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 160  # Минимальное значение R
    g_max = 185  # Максимальное значение G
    b_max = 185  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("атакую")
        return True
    else:
        print("поиск целей")
        return False

async def check_lock(): #Проверка на пикселя красного цвета, при закрытом овервью, непись в гриде.
    capture_screenshot()
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 926  # Координата x
    y = 214  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 200  # Минимальное значение R
    g_max = 60  # Максимальное значение G
    b_max = 85  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("обнаружена волна")
        return True
    else:
        print("ожидаю цели")
        return False

async def check_open_over(): #Проверка открыто ли овервью, серый пиксель, если открыто закрываем его
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 688  # Координата x
    y = 302  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 150  # Минимальное значение R
    g_max = 165  # Максимальное значение G
    b_max = 165  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("овервью закрыто")
        return True
    else:
        return False

async def check_autopilot(): # Проверка на автопилот, если не установлен пишем в дискорд
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 198  # Координата x
    y = 150  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 145  # Минимальное значение R
    g_max = 165  # Максимальное значение G
    b_max = 175  # Максимальное значение B
    if not (r > r_min and g < g_max and b < b_max):
        print("атопилот не установлен")
        return True
    else:
        print("авопилот установлен")
        return False

async def check_in_dock():     # Проверка на док ##############################################
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 820  # Координата x
    y = 172  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 168  # Минимальное значение R
    g_max = 150  # Максимальное значение G
    b_max = 45  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("обнаружен док")
        return True
    else:
        print("док не обнаружен")
        return False

async def check_enemies(): #Проверка наличия врагов в системе
    cv2.imwrite(current_file, process_image('screenshot.png'))
    img1 = cv2.imread(previous_file)
    img2 = cv2.imread(current_file)
    diff = cv2.absdiff(img1, img2)
    nonzero_count = np.count_nonzero(diff)
    #print(nonzero_count)
    if nonzero_count >= 175:
        #print(f"Различие пикселей: {nonzero_count}")
        return True
    else:
        #print("Угроз не обнаружено")
        return False

async def check_asteroid(): #Проверка на наличие астероидов в гриде
    capture_screenshot()
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 934  # Координата x
    y = 105  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 148  # Минимальное значение R
    g_max = 158  # Максимальное значение G
    b_max = 158  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("обнаружены астероиды")
        return True
    else:
        print("Ищу астероиды")
        return False

async def check_asteroid2(): #Проверка на наличие астероидов в гриде
    capture_screenshot()
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 934  # Координата x
    y = 59  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 145  # Минимальное значение R
    g_max = 160  # Максимальное значение G
    b_max = 160  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("обнаружены астероиды")
        return True
    else:
        print("ищу астероиды")
        return False

async def check_swipe(): #Проверка на необходимость свайпа и свайп
    capture_screenshot()
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 32  # Координата x
    y = 62  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 190  # Минимальное значение R
    g_max = 215  # Максимальное значение G
    b_max = 215  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("Свайпаю карго")
        await swipe()
        return True
    else:
        return False

async def check_cargo(): #проверка на полное карго
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 21  # Координата x
    y = 72  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 55  # Минимальное значение R
    g_max = 115  # Максимальное значение G
    b_max = 120  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        print("трюм заполнен")
        return True
    else:
        print("трюм не полон")
        return False

async def findapproach(): #Найти апроч
    keywords = "Approach"
    await find(keywords)

async def findasteroid(): #найти астероид
    keywords = "Asteroid"
    await find(keywords)

async def findwarp(): #найти варп
    keywords = "Warp,arp,war,WARP,War"
    await find(keywords)

async def findsmall(): #найти маленькую
    keywords = "Small,small,SmaII,smaII,mall,Medium,medium,Large,large"
    await find(keywords)

async def check_enemy_shield():
    first_module = (650, 497)
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 929  # Координата x
    y = 56  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 160  # Минимальное значение R
    g_max = 185  # Максимальное значение G
    b_max = 185  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        #tap_random(first_module)
        return True
    else:
        return False

async def main_processor():
    image_path = "screenshot.png"
    img = cv2.imread(image_path)
    x = 926  # Координата x
    y = 214  # Координата y
    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
    r_min = 200  # Минимальное значение R
    g_max = 60  # Максимальное значение G
    b_max = 85  # Максимальное значение B
    # print("Значения RGB пикселя:", r, g, b)
    if r > r_min and g < g_max and b < b_max:
        # print("Лочим непись")
        await processlock()
        await asyncio.sleep(2)
    else:
        await adb.openover()
        await asyncio.sleep(1)
        await findsmall()
        await asyncio.sleep(1)
        await findwarp()
        await asyncio.sleep(1)
        await adb.closeover()
        await asyncio.sleep(25)

def add_watermark(image_path):
    img = PIL.Image.open(image_path)
    draw = PIL.ImageDraw.Draw(img)
    font = PIL.ImageFont.truetype('eve.ttf', size=30)
    time_str = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    draw.text((50, 50), time_str, font=font, fill=(255, 255, 255, 128))
    img.save(image_path)

def add_grid_to_screenshot(screenshot_file, grid_size):
    screenshot = cv2.imread(screenshot_file)
    height, width, _ = screenshot.shape
    square_width = width // grid_size[0]
    square_height = height // grid_size[1]
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            x1 = i * square_width
            y1 = j * square_height
            x2 = (i + 1) * square_width
            y2 = (j + 1) * square_height
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.putText(screenshot, f'{i * grid_size[1] + j}', (center_x - 10, center_y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            globals()[f'coord_{i * grid_size[1] + j}'] = (center_x, center_y)
            cv2.rectangle(screenshot, (x1, y1), (x2, y2), (0, 255, 0), 1)
    cv2.imwrite('coords.png', screenshot)