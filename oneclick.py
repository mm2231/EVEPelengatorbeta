import subprocess
import sys
import random
import cv2
import numpy as np
import pygame
import traceback
import discord
import configparser
from discord.ext import commands
import asyncio
import keyboard
import json
import requests
import pytesseract

uuid = subprocess.check_output('wmic csproduct get UUID').decode('utf-8').split()[1]
with open('auth.txt', 'r') as file:
    auth_data = file.read().splitlines()
    login = auth_data[0]
    password = auth_data[1]
request = requests.get(f'http://109.233.59.3:8080/api/checkaccess?login={login}&password={password}&uuid={uuid}')
try:
    string = json.loads(str(request.text))
except Exception as e:
    print(e)
else:
    if string['response'] == 'Access Granted':
        print('Доступ разрешен')
    else:
        print('Доступ запрещен')
        exit()

config = configparser.ConfigParser()
config.read('config.ini')
stop_flag = config.getboolean('Bot', 'stop_flag', fallback=False)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

adb_path = r'platform-tools/adb.exe'
device_id = None
lock = 'lock.png'
current_lock = 'locktrue.png'
previous_file = '1.png'
current_file = '2.png'
image_path = "screenshot.png"
crop_coords = (1, 415, 185, 450) #local
crop_coords2 = (585, 329, 614, 357) #masslock
crop_coords3 = (725, 40, 915, 300) #watermarks
click_coords = (20, 147)  # автопилот
click_coords2 = (600, 343) # masslock
click_coords3 = (884, 180) # andock
click_coords4 = (478, 471) # zoom
click_coords5 = (923, 440) # ИИ ядро
click_coords6 = (80, 226) #установка АП
click_coords7 = (300, 190) #установка деста
click_coords8 = (187, 187) #закрываем окно букмарок
click_coords9 = (52, 509) #открыть локальный чат
click_coords10 = (478, 419) #логин
click_coords11 = (264, 134) #Тап по персонажу 1
click_coords12 = (856, 280) #Фокус огонь
click_coords13 = (910, 37) #фокус
click_coords14 = (924, 302) #развернуть овервью
two = (818, 120) #2 аномалия с верху
click_coords16 = (689, 302) #скрыть открытое овервью
click_coords17 = (648, 183) #Варп на 2
one = (823, 69) #первая анома
warpone = (647, 129) #Варп на 1
three = (823, 173) #3
warpthree = (640, 236) #Варп на 3
four = (823, 221) #4
warpfour = (641, 286) #Варп на 4
five = (820, 275) #5
warpfive = (643, 340) #варп на 5
six = (818, 313) #6
warpsix = (650, 390) #Варп на 6
offset_x = random.randint(-5, 5)
offset_y = random.randint(-5, 5)
click_coords2 = (click_coords2[0] + offset_x, click_coords2[1] + offset_y)
should_convert_to_black_and_white = True
authentication = None

adb_devices_cmd = f"{adb_path} devices"
output = subprocess.check_output(adb_devices_cmd.split()).decode()
devices = output.strip().split("\n")[1:]

if not devices:
    print("Устройство не найдено в ADB...")
    raise Exception("Не удалось подключиться к устройству через ADB.")
print("Список устройств, подключенных к ADB:")
print("\n".join(devices))

for d in devices:
    if d.endswith("device"):
        device_id = d.split("\t")[0]
        break

if not device_id:
    print("Не удалось найти эмулятор в списке устройств...")
    raise Exception("Не удалось подключиться к эмулятору через ADB.")
else:
    print("Подключился к эмулятору...")
    pygame.mixer.init()
    pygame.mixer.music.load("connecting.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

@bot.event
async def on_ready():
    print(f'Покрабим?')
    capture_screenshot()
    await asyncio.sleep(1)
    image_path = 'screenshot.png'

image = cv2.imread('screenshot.png')  # Загрузка изображения
image_height, image_width, _ = image.shape  # Определение размеров изображения

def tap_random(coords):
    prop_x = coords[0] / image_width
    prop_y = coords[1] / image_height

    random_x = random.uniform(prop_x - 0.01, prop_x + 0.01)
    random_y = random.uniform(prop_y - 0.01, prop_y + 0.01)

    subprocess.run(
        [adb_path, '-s', device_id, 'shell', 'input', 'tap', str(random_x * image_width), str(random_y * image_height)],
        stdout=subprocess.DEVNULL)

@bot.command()
async def starteve(ctx):
    adb_path = r'C:/platform-tools/adb.exe'
    command = f'{adb_path} shell am start -n com.netease.eve.en/com.netease.ntunisdk.base.deeplink.UniDeepLinkActivity'
    try:
        subprocess.run(command, shell=True, check=True)
        print("Приложение успешно запущено")
    except subprocess.CalledProcessError:
        print("Ошибка при запуске приложения")
    await ctx.send("Запускаю клиент игры")

@bot.command()
async def closeeve(ctx):
    adb_path = "C:/platform-tools/adb.exe"
    package_name = "com.netease.eve.en"
    command = f'{adb_path} shell am force-stop {package_name}'
    try:
        subprocess.run(command, shell=True, check=True)
        await ctx.send("Приложение успешно закрыто")
    except subprocess.CalledProcessError:
        await ctx.send("Ошибка при закрытии приложения")

@bot.command()
async def restart(ctx):
    await ctx.send("Перезапуск скрипта, все функции отключены")
    subprocess.Popen([sys.executable, "restart_script.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    await bot.close()

@bot.command()
async def closeover(ctx):
    tap_random(click_coords16)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    await ctx.send("Закрываю оверьвью")

@bot.command()
async def хелп(ctx):
    command_list = {
        "!start": "Запускает цикл мониторинга за врагами, если в локале враг, поступает команда в док, также прокликивается автоприцел и фокус",
        "!stop": "Останавливает мониторинг врагов и автоприцеливание",
        "!dock": "Кликает по установленному автопилоту",
        "!pilot": "Устанавливает автопилот, первая бука из списка",
        "!core": "Включает либо отключает ИИ ядро",
        "!zoom": "Отдаляет либо приближает камеру",
        "!screen": "Делает скриншот и высылает в чат",
        "!local": "Открывает локальный чат",
        "!undock": "Выйти из дока",
        "!restart": "Полная перезагрузка скрипта",
        "!starteve": "Запуск клиента EVE Echoes",
        "!closeeve": "Закрытие клиента EVE Echoes",
        "!login": "залогинится с вступительного экрана",
        "!closeover": "Закрыть овервью",
        "!next и warp": "Эксперементальные функции варпа на аномалии"
    }
    message = "Список команд:\n"
    for command, description in command_list.items():
        message += f"{command}: {description}\n"
    await ctx.send(message)

@bot.command()
async def press(ctx, key: str):
    keyboard.send(key)
    await ctx.send(f'Клавиша {key} нажата и отпущена')

def capture_screenshot():
    subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
    subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screenshot.png'],
                   stdout=subprocess.DEVNULL)

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

def convert_to_black_and_white(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, black_and_white = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return black_and_white

stop_flag = False

@bot.command()
async def login(ctx):
    await ctx.send("логинюсь")
    tap_random(click_coords10)
    await asyncio.sleep(13)
    tap_random(click_coords11)

@bot.command()
async def dock(ctx):
    global stop_flag
    stop_flag = True
    await ctx.send("Докаюсь")
    tap_random(click_coords)
    pygame.mixer.init()
    pygame.mixer.music.load("alarm.mp3")
    pygame.mixer.music.play()
    await asyncio.sleep(1)
    capture_screenshot()
    try:
        with open('screenshot.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    except FileNotFoundError:
        await ctx.send('Файл screenshot.png не найден.')

@bot.command()
async def pilot(ctx):
    global stop_flag
    stop_flag = True
    await ctx.send("Устанавливаю автопилот")
    tap_random(click_coords)
    await asyncio.sleep(1.5)
    tap_random(click_coords6)
    await asyncio.sleep(1.5)
    tap_random(click_coords7)
    await asyncio.sleep(1.5)
    tap_random(click_coords8)
    capture_screenshot()
    try:
        with open('screenshot.png', 'rb') as f:
            picture = discord.File(f)
            await asyncio.sleep(1)
            await ctx.send(file=picture)
    except FileNotFoundError:
        await ctx.send('Файл screenshot.png не найден.')

@bot.command()
async def core(ctx):
    await ctx.send("Включаю ядро")
    tap_random(click_coords5)

@bot.command()
async def local(ctx):
    await ctx.send("Открываю локальный чат")
    tap_random(click_coords9)
    await asyncio.sleep(1)
    capture_screenshot()
    try:
        with open('screenshot.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    except FileNotFoundError:
        await ctx.send('Файл screenshot.png не найден.')

@bot.command()
async def screen(ctx):
    try:
        subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
        subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screen.png'],
                       stdout=subprocess.DEVNULL)
        await asyncio.sleep(1)
        with open('screen.png', 'rb') as f:
            image = discord.File(f, filename='screen.png')
            await ctx.send(file=image)
    except FileNotFoundError:
        await ctx.send('Скрин не найден.')

stop_flag = False

@bot.command()
async def stop(ctx):
    global stop_flag
    stop_flag = True
    await ctx.send("Поиск врагов и автолок выключен")
    config.set('Bot', 'stop_flag', str(stop_flag))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

async def lock():
    tap_random(click_coords2)
    delay = random.uniform(1, 3)
    await asyncio.sleep(delay)

async def focus():
    tap_random(click_coords13)
    await asyncio.sleep(1)
    tap_random(click_coords12)
    delay = random.uniform(1, 2)
    await asyncio.sleep(delay)

@bot.command()
async def zoom(ctx):
    tap_random(click_coords4)
    await ctx.send("Зум камеры, проверьте на скриншоте положение, если нужно повторите команду")
    await asyncio.sleep(1)
    await screen(ctx)

@bot.command()
async def undock(ctx):
    await ctx.send("Андокаюсь")
    tap_random(click_coords3)
    await asyncio.sleep(10)
    await screen(ctx)

def setwatermarks(image_path, crop_coords3, watermarks):
    capture_screenshot()
    img = cv2.imread(image_path)
    x, y, w, h = crop_coords3
    cropped_img = img[y:y+h, x:x+w]
    for watermark in watermarks:
        text, coords, color, font_size = watermark
        x, y = coords
        cv2.putText(
            cropped_img,
            text,
            coords,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            color,
            2,
            cv2.LINE_AA
        )
    output_path = f"Anomaly_{image_path}"
    cv2.imwrite(output_path, cropped_img)
    return output_path

stop_flag = False

@bot.command()
async def next(ctx):
    global stop_flag
    stop_flag = True
    tap_random(click_coords14)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    watermarks = [
        ("1", (180, 30), (0, 0, 255), 0.6),
        ("2", (180, 80), (0, 0, 255), 0.6),
        ("3", (180, 130), (0, 0, 255), 0.6),
        ("4", (180, 180), (0, 0, 255), 0.6),
        ("5", (180, 230), (0, 0, 255), 0.6),
        ("6", (180, 280), (0, 0, 255), 0.6),
    ]
    output_image_path = setwatermarks(image_path, crop_coords3, watermarks)
    print("Обработанное изображение сохранено:", output_image_path)
    await asyncio.sleep(1)
    await ctx.send("Выбери аномалию")
    with open('Anomaly_screenshot.png', 'rb') as f:
        image = discord.File(f, filename='Anomaly_screenshot.png')
        await ctx.send(file=image)

stop_flag = True

@bot.command()
async def start(ctx):
    global stop_flag
    stop_flag = False
    while not bot.is_closed() and not stop_flag:
        await ctx.send("Включен поиск врагов, автолок и focusfire")
        await ctx.send("Проверь автопилот")
        try:
            capture_screenshot()
            cv2.imwrite(previous_file, process_image('screenshot.png'))
            while not stop_flag:
                capture_screenshot()
                cv2.imwrite(current_file, process_image('screenshot.png'))
                img1 = cv2.imread(previous_file)
                img2 = cv2.imread(current_file)
                diff = cv2.absdiff(img1, img2)
                if np.count_nonzero(diff) / diff.size >= 0.008:
                    diff_percent = (np.count_nonzero(diff) / diff.size) * 100
                    print(f'Террористическая угроза {diff_percent:.2f}%')
                    await ctx.send("Террористическая угроза")
                    await ctx.send("Докаюсь")
                    tap_random(click_coords)
                    cv2.imwrite('3.png', diff)
                    pygame.mixer.init()
                    pygame.mixer.music.load("alarm.mp3")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        with open('screenshot.png', 'rb') as f:
                            picture = discord.File(f)
                            await ctx.send(file=picture)
                        continue
                    return
                else:
                    #print('Все в порядке')
                    await asyncio.sleep(1)
                    image_path = "screenshot.png"
                    img = cv2.imread(image_path)
                    x = 926  # Координата x
                    y = 214  # Координата y
                    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
                    r_min = 200  # Минимальное значение R
                    g_max = 60  # Максимальное значение G
                    b_max = 85  # Максимальное значение B
                    #print("Значения RGB пикселя:", r, g, b)
                    if r > r_min and g < g_max and b < b_max:
                        #print("Лочим непись")
                        await processlock()
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
                            await focus()
        except Exception as e:
            print("Произошла ошибка:")
            traceback.print_exc()
            with open("error_log.txt", "a") as f:
                f.write("Произошла ошибка:\n")
                f.write(traceback.format_exc())
        await asyncio.sleep(1)

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

@bot.command()
async def warp(ctx, number: int):
    if number == 1:
        await ctx.send('Варпаю на 1')
        tap_random(one)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(warpone)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords16)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)

    elif number == 2:
        await ctx.send('Варпаю на 2')
        tap_random(two)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords17)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords16)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)

    elif number == 3:
        await ctx.send('Варпаю на 3')
        tap_random(three)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(warpthree)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords16)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)

    elif number == 4:
        await ctx.send('Варпаю на 4')
        tap_random(four)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(warpfour)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords16)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)

    elif number == 5:
        await ctx.send('Варпаю на 5')
        tap_random(five)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(warpfive)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords16)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)

    elif number == 6:
        await ctx.send('Варпаю на 6')
        tap_random(six)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(warpsix)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)
        tap_random(click_coords16)
        delay = random.uniform(1.5, 2)
        await asyncio.sleep(delay)

    else:
        await ctx.send('Редиска, нужно писать от 1 до 6')

stop_flag = True

@bot.command()
async def mine(ctx):
    global stop_flag
    stop_flag = False
    while not bot.is_closed() and not stop_flag:
        await ctx.send("Включен поиск врагов, тихо грызем камни!")
        await ctx.send("Проверь автопилот, редиска.")
        try:
            capture_screenshot()
            cv2.imwrite(previous_file, process_image('screenshot.png'))
            while not stop_flag:
                capture_screenshot()
                cv2.imwrite(current_file, process_image('screenshot.png'))
                img1 = cv2.imread(previous_file)
                img2 = cv2.imread(current_file)
                diff = cv2.absdiff(img1, img2)
                if np.count_nonzero(diff) / diff.size >= 0.008:
                    diff_percent = (np.count_nonzero(diff) / diff.size) * 100
                    print(f'Террористическая угроза {diff_percent:.2f}%')
                    await ctx.send("Террористическая угроза")
                    await ctx.send("Докаюсь")
                    tap_random(click_coords)
                    cv2.imwrite('3.png', diff)
                    pygame.mixer.init()
                    pygame.mixer.music.load("alarm.mp3")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        with open('screenshot.png', 'rb') as f:
                            picture = discord.File(f)
                            await ctx.send(file=picture)
                        continue
                    return
                else:
                    #print('Все в порядке')
                    await asyncio.sleep(1)
                    image_path = "screenshot.png"
                    img = cv2.imread(image_path)
                    x = 32  # Координата x
                    y = 62  # Координата y
                    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
                    r_min = 190  # Минимальное значение R
                    g_max = 215  # Максимальное значение G
                    b_max = 215  # Максимальное значение B
                    #print("Значения RGB пикселя:", r, g, b)
                    if r > r_min and g < g_max and b < b_max:
                        #print("Свайпаю карго")
                        await swipe()
                    image_path = "screenshot.png"
                    img = cv2.imread(image_path)
                    x = 21  # Координата x
                    y = 72  # Координата y
                    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
                    r_min = 55  # Минимальное значение R
                    g_max = 115  # Максимальное значение G
                    b_max = 120  # Максимальное значение B
                    #print("Значения RGB пикселя:", r, g, b)
                    if r > r_min and g < g_max and b < b_max:
                        await dock(ctx)
                        await ctx.send("Карго полное, Не забудь выгрузится")
        except Exception as e:
            print("Произошла ошибка:")
            traceback.print_exc()
            with open("error_log.txt", "a") as f:
                f.write("Произошла ошибка:\n")
                f.write(traceback.format_exc())
        await asyncio.sleep(1)

async def swipe():
    start_x = 21  # X-координата начала свайпа
    start_y = 88  # Y-координата начала свайпа
    end_x = 210  # X-координата конца свайпа
    end_y = 89  # Y-координата конца свайпа
    duration = 500  # Длительность свайпа в миллисекундах
    subprocess.run([adb_path, '-s', device_id, 'shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y),
     str(duration)],
                  stdout=subprocess.DEVNULL)

@bot.command()
async def harvest(ctx):
    drill1 = (650, 495)
    drill2 = (705, 495)
    drill3= (760, 495)
    drill4 = (815, 495)
    drill5 = (868, 495)
    tap_random(drill1)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    tap_random(drill2)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    tap_random(drill3)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    tap_random(drill4)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    tap_random(drill5)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    await ctx.send("Буры/дроны запущены.")

@bot.command()
async def unload(ctx):
    cargo = (20, 89)
    shiphold = (108, 416)
    selectall = (734, 490)
    moveto = (110, 114)
    station = (382, 122)
    closewindow = (925, 30)
    tap_random(cargo)
    delay = random.uniform(2, 3)
    await asyncio.sleep(delay)
    tap_random(shiphold)
    delay = random.uniform(2, 3)
    await asyncio.sleep(delay)
    tap_random(selectall)
    delay = random.uniform(2, 3)
    await asyncio.sleep(delay)
    tap_random(moveto)
    delay = random.uniform(2, 3)
    await asyncio.sleep(delay)
    tap_random(station)
    delay = random.uniform(2, 3)
    await asyncio.sleep(delay)
    tap_random(closewindow)
    delay = random.uniform(2, 3)
    await asyncio.sleep(delay)
    await ctx.send("Вроде бы как выгрузился.")

async def miner():
    await swipe()
    await asyncio.sleep(1)

stop_flag = True

@bot.command()
async def crab(ctx):
    global stop_flag
    stop_flag = False
    while not bot.is_closed() and not stop_flag:
        await ctx.send("Включен монитор щита, автолок и focusfire")
        await ctx.send("Проверь автопилот")
        try:
            capture_screenshot()
            cv2.imwrite(previous_file, process_image('screenshot.png'))
            while not stop_flag:
                capture_screenshot()
                image_path = "screenshot.png"
                img = cv2.imread(image_path)
                x = 486  # Координата x
                y = 424  # Координата y
                b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
                r_min = 95  # Минимальное значение R
                g_max = 30  # Максимальное значение G
                b_max = 25  # Максимальное значение B
                #print("Значения RGB пикселя:", r, g, b)
                if r > r_min and g < g_max and b < b_max:
                    await ctx.send(f'Щиты на исходе')
                    await ctx.send("Докаюсь")
                    tap_random(click_coords)
                    pygame.mixer.init()
                    pygame.mixer.music.load("alarm.mp3")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        with open('screenshot.png', 'rb') as f:
                            picture = discord.File(f)
                            await ctx.send(file=picture)
                        continue
                    return
                else:
                    #print('Все в порядке')
                    await asyncio.sleep(1)
                    image_path = "screenshot.png"
                    img = cv2.imread(image_path)
                    x = 926  # Координата x
                    y = 214  # Координата y
                    b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
                    r_min = 200  # Минимальное значение R
                    g_max = 60  # Максимальное значение G
                    b_max = 85  # Максимальное значение B
                    #print("Значения RGB пикселя:", r, g, b)
                    if r > r_min and g < g_max and b < b_max:
                        #print("Лочим непись")
                        await processlock()
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
                            await focus()
                    #else:

        except Exception as e:
            print("Произошла ошибка:")
            traceback.print_exc()
            with open("error_log.txt", "a") as f:
                f.write("Произошла ошибка:\n")
                f.write(traceback.format_exc())
        await asyncio.sleep(1)


def crop_image2(image_path, coordinates):
    # Загрузка изображения в ч/б формате
    img = cv2.imread(image_path, 0)

    # Обрезка изображения по указанным координатам
    x, y, w, h = coordinates
    cropped_img = img[y:y + h, x:x + w]

    # Бинаризация изображения
    _, binary_img = cv2.threshold(cropped_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Разделение изображения на 5 областей
    height, width = binary_img.shape
    step = int(width / 5)
    regions = []

    for i in range(5):
        start = i * step
        end = start + step
        region_img = binary_img[0:height, start:end]
        regions.append(region_img)
        cv2.rectangle(binary_img, (start, 0), (end, height), (0, 255, 0),
                      2)
    mid_points = []
    for i, region_img in enumerate(regions):
        _, contours, hierarchy = cv2.findContours(region_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            mid_x = int(M["m10"] / M["m00"]) + start
            mid_points.append(mid_x)

    return mid_points

@bot.command()
async def process_regions(image_path, coordinates):
    mid_points = crop_image2(image_path, coordinates)

    for mid_x in mid_points:
        # Обработка каждой области с помощью pytesseract
        # ...
        text = pytesseract.image_to_string(image)
        # ...

        # Проверка наличия слов "large", "medium", "small"
        keywords = ["large", "medium", "small"]
        has_keyword = False
        for keyword in keywords:
            if keyword in text.lower():
                has_keyword = True
                break
        # Если найдено ключевое слово, кликнуть по области с помощью adb
        if has_keyword:
            # Выполнение команды adb
            adb_command = f"adb shell input tap {mid_x} <y-координата>"
            subprocess.run(adb_command, shell=True)


# Пример вызова функции
image_path = "screenshot.png"
coordinates = (757, 45, 912, 300)  # Пример координат (x, y, ширина, высота)

process_regions(image_path, coordinates)

if __name__ == "__main__":
    with open("auth.txt", "r") as file:
        token = auth_data[2]
    bot.run(token)

