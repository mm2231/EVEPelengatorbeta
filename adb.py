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

def check_device_connection(device_id):
    result = subprocess.run([adb_path, '-s', device_id, 'devices'], capture_output=True, text=True)
    output = result.stdout.strip()
    if f"{device_id}\tdevice" in output:
        return True
    return False

def check_app_running(device_id):
    result = subprocess.run([adb_path, '-s', device_id, 'shell', 'dumpsys', 'window', 'windows'], capture_output=True, text=True)
    output = result.stdout.strip()
    if "com.netease.eve.en" in output:
        return True
    return False

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
    tap_random(click_coords3)

async def nanocore():
    skill = (570, 445)
    print("Жму на скилл ядра.")
    tap_random(skill)

async def zoom():
    tap_random(click_coords4)
    print("Зумим камеру")

async def openlocal():
    tap_random(click_coords9)

async def core():
    print("Активация крайнего правого модуля с верху")
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

async def openover():
    tap_random(click_coords14)
    delay = random.uniform(1, 2)
    await asyncio.sleep(delay)

async def login():
    print("Логинюсь")
    tap_random(click_coords10)
    await asyncio.sleep(13)
    tap_random(click_coords11)

async def dock():
    print("Докаюсь")
    tap_random(click_coords)



