import subprocess
import asyncio
import random
import cv2
import discord
from discord.ext import commands
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

adb_path = r'platform-tools/adb.exe'
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
click_coords16 = (689, 302) #скрыть открытое овервью

config_file = 'config.txt'
device_id = None

with open(config_file, 'r') as file:
    for line in file:
        if 'device_id' in line:
            device_id = line.split('=')[1].strip()

if device_id is not None:
    print(device_id)
else:
    print("Значение device_id не найдено.")

'''
adb_devices_cmd = f"{adb_path} devices"
output = subprocess.check_output(adb_devices_cmd.split()).decode()

devices = output.strip().split("\n")[1:]

if not devices:
    print("Устройство не найдено...")
    raise Exception("Ошибка подключения к ADB.")


def select_device(devices):
    if len(devices) == 1:
        return devices[0].split("\t")[0]

    print("Список устройств ADB:")
    for i, d in enumerate(devices):
        print(f"{i + 1}. {d}")

    while True:
        try:
            index = int(input("Выбери устройство: ")) - 1
            if 0 <= index < len(devices):
                return devices[index].split('\t')[0]
        except ValueError:
            pass

        print("Неверный выбор")


device_id = None
for d in devices:
    if d.endswith("Устройство"):
        device_id = d.split("\t")[0]
        break

if not device_id:
    device_id = select_device(devices)
    if not device_id:
        print("Could not find the emulator in the device list...")
        raise Exception("Failed to connect to emulator via ADB.")
else:
    print("Подключился...")
'''

#старая версия под эмулятор
def tap_random(coords):
    capture_screenshot()
    image = cv2.imread('screenshot.png')  # Загрузка изображения
    image_height, image_width, _ = image.shape  # Определение размеров изображения

    prop_x = coords[0] / image_width
    prop_y = coords[1] / image_height

    random_x = random.uniform(prop_x - 0.01, prop_x + 0.01)
    random_y = random.uniform(prop_y - 0.01, prop_y + 0.01)

    subprocess.run(
        [adb_path, '-s', device_id, 'shell', 'input', 'tap', str(random_x * image_width), str(random_y * image_height)],
        stdout=subprocess.DEVNULL)

def tap_cortage(x, y):
    capture_screenshot()
    image = cv2.imread('screenshot.png')
    image_height, image_width, _ = image.shape

    prop_x = x / image_width
    prop_y = y / image_height

    random_x = random.uniform(prop_x - 0.01, prop_x + 0.01)
    random_y = random.uniform(prop_y - 0.01, prop_y + 0.01)

    subprocess.run(
        [adb_path, '-s', device_id, 'shell', 'input', 'tap', str(random_x * image_width), str(random_y * image_height)],
        stdout=subprocess.DEVNULL)

def capture_screenshot():
    subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
    subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screenshot.png'],
                   stdout=subprocess.DEVNULL)

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

def click_on_coordinate(coord_number):
    center_x, center_y = globals()[f'coord_{coord_number}']
    tap_random((center_x, center_y))

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

async def swipe():
    start_x = 21  # X-координата начала свайпа
    start_y = 88  # Y-координата начала свайпа
    end_x = 210  # X-координата конца свайпа
    end_y = 89  # Y-координата конца свайпа
    duration = 500  # Длительность свайпа в миллисекундах
    subprocess.run([adb_path, '-s', device_id, 'shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y),
     str(duration)],
                  stdout=subprocess.DEVNULL)

async def unload(): #Разгрузка карго в доке
    cargo = (20, 89)
    shiphold = (108, 416)
    selectall = (734, 490)
    moveto = (110, 114)
    station = (382, 122)
    closewindow = (925, 30)
    tap_random(cargo)
    delay = random.uniform(3, 4)
    await asyncio.sleep(delay)
    #tap_random(shiphold)
    #delay = random.uniform(2, 3)
    #await asyncio.sleep(delay)
    tap_random(selectall)
    delay = random.uniform(3, 4)
    await asyncio.sleep(delay)
    tap_random(moveto)
    delay = random.uniform(3, 4)
    await asyncio.sleep(delay)
    tap_random(station)
    delay = random.uniform(3, 4)
    await asyncio.sleep(delay)
    tap_random(closewindow)

async def module(): #Активация 5 нижних модулей
    drill1 = (650, 495)
    drill2 = (705, 495)
    drill3= (760, 495)
    drill4 = (815, 495)
    drill5 = (868, 495)
    tap_random(drill1)
    delay = random.uniform(0.5, 1)
    await asyncio.sleep(delay)
    tap_random(drill2)
    delay = random.uniform(0.5, 1)
    await asyncio.sleep(delay)
    tap_random(drill3)
    delay = random.uniform(0.5, 1)
    await asyncio.sleep(delay)
    tap_random(drill4)
    delay = random.uniform(0.5, 1)
    await asyncio.sleep(delay)
    tap_random(drill5)

async def undock():
    print("Выхожу из дока.")
    tap_random(click_coords3)

async def zoom():
    tap_random(click_coords4)
    print("Зумим камеру")

async def openlocal():
    print("открываю локал")
    tap_random(click_coords9)

async def core():
    print("Включаю ядро")
    tap_random(click_coords5)

async def pilot():
    print("Устонавливаю автопилот")
    tap_random(click_coords)
    await asyncio.sleep(3)
    tap_random(click_coords6)
    await asyncio.sleep(3)
    tap_random(click_coords7)
    await asyncio.sleep(3)
    tap_random(click_coords8)

async def closeover():
    tap_random(click_coords16)
    delay = random.uniform(1.5, 2)
    await asyncio.sleep(delay)
    print("Закрываю овервью")

async def openover():
    tap_random(click_coords14)
    delay = random.uniform(1, 2)
    await asyncio.sleep(delay)
    print("Открываю овервью")

async def login():
    print("Логинюсь")
    tap_random(click_coords10)
    await asyncio.sleep(13)
    tap_random(click_coords11)

async def dock():
    print("Докаюсь")
    tap_random(click_coords)

async def tap(ctx, square_number):
    square_number = int(square_number)
    if f'coord_{square_number}' in globals():
        click_on_coordinate(square_number)
        await ctx.send('click clack')
    else:
        await ctx.send('Wrong square number')
