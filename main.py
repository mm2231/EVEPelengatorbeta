import asyncio
import os
import shutil
import subprocess
import sys
import traceback
import cv2
import discord
import keyboard
import numpy as np
import psutil
import pygetwindow as gw
import pytesseract
import pyttsx3
from discord.ext import commands


import adb
import imageworks
from adb import capture_screenshot, tap_random, click_coords

adb_path = r'platform-tools/adb.exe'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
previous_file = '1.png'
current_file = '2.png'
crop_coordss = [(35, 325, 725, 960), (169, 459, 0, 188), (0, 120, 106, 724)]
crop_x1, crop_y1, crop_x2, crop_y2 = 1, 480, 273, 534
crop_dx1, crop_dy1, crop_dx2, crop_dy2 = 373, 170, 550, 197    #корабль
crop_cx1, crop_cy1, crop_cx2, crop_cy2 = 373, 143, 550, 169    #никнейм
local_file = 'local.png'
config_file = 'config.txt'
current_status = 'Ожидание команды'
looping = False
mining = False
dock = False
space = False
voice_client = None
voicechannel = None
device_id = None
token = None
channels = None

with open(config_file, 'r') as file:
    for line in file:
        if 'device_id' in line:
            device_id = line.split('=')[1].strip()
if device_id is not None:
    pass
else:
    print("Значение device_id не найдено.")

'''
adb_devices_cmd = f"{adb_path} devices"
output = subprocess.check_output(adb_devices_cmd.split()).decode()
devices = output.strip().split("\n")[1:]

def select_device(devices):
    if len(devices) == 1:
        return devices[0].split("\t")[0]
    print("List of devices connected to ADB:")
    for i, d in enumerate(devices):
        print(f"{i+1}. {d.replace('/t', '')}")
    device_choice = input("Select the device: ")
    try:
        index = int(device_choice) - 1
        return devices[index].split('\t')[0]
    except (ValueError, IndexError):
        print("Incorrect selection")
        return devices[0].split("\t")[0]
if not devices:
    print("Device not found in ADB...")
    raise Exception("Failed to connect to the device via ADB.")
device_id = None
print("\n".join(devices))
for d in devices:
    if d.endswith("device"):
        device_id = d.split("\t")[0]
        break
device_id = select_device(devices)
if not device_id:
    print("Could not find the emulator in the device list...")
    raise Exception("Failed to connect to emulator via ADB.")
else:
    print("Connected to the emulator...")'''

#system functions
@bot.command()
async def selfdestruction(ctx):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'config.txt')
    # Проверка идентификатора пользователя
    if ctx.author.id != 663106596825595917:
        await ctx.send("У вас нет разрешения на выполнение этой команды.")
        return

    if os.path.exists(file_path):
        await ctx.send("Запускаю самоуничтожение скрипта")

        await ctx.author.send(file=discord.File(file_path))

        os.remove(file_path)
        sys.exit(0)
    else:
        await ctx.send("Ошибка")
        sys.exit(1)

@bot.command()
async def getconfig(ctx):
    if not os.path.exists("config.txt"):
        await ctx.send("Файл конфигурации не найден.")

    await ctx.send(file=discord.File("config.txt"))

async def update_config_file(uploaded_file):
    # Проверка наличия файла config.txt
    if not os.path.exists("config.txt"):
        return "Файл config.txt не найден."

    # Сохранение загруженного файла
    temp_file_path = "temp_config.txt"
    with open(temp_file_path, "wb") as file:
        file.write(await uploaded_file.read())

    # Замена файла config.txt
    shutil.copy(temp_file_path, "config.txt")

    # Удаление временного файла
    os.remove(temp_file_path)

    return "Конфигурация обновлена."

@bot.command()
async def updateconfig(ctx):
    # Проверка наличия вложения
    if len(ctx.message.attachments) == 0:
        await ctx.send("Вы должны прикрепить файл для обновления config.txt.")
        return

    # Получение первого вложенного файла
    attachment = ctx.message.attachments[0]

    # Проверка расширения файла
    if not attachment.filename.endswith(".txt"):
        await ctx.send("Неверный формат файла. Поддерживаются только текстовые файлы.")
        return

    # Вызов функции обновления файла
    response = await update_config_file(attachment)
    await ctx.send(response)

@bot.command()
async def system(ctx):
    cpu_load, memory_usage, windows_column = get_system_stats()
    await ctx.send(f"Загрузка ЦПУ: {cpu_load}%")
    await ctx.send(f"Использовано оперативной памяти: {memory_usage}%")
    await ctx.send(f"Запущенные эмуляторы: \n{windows_column}")

@bot.command()
async def restartadb(ctx):
    if looping:
        await ctx.send("Нельзя перезапускать сервер при работе цикла start, отключите мониторинг")
    else:
        try:
            await ctx.send("Инициализирую перезагрузку сервера ADB. Ожидайте!")
            subprocess.run([adb_path, 'kill-server'])
            await asyncio.sleep(1)
            subprocess.run([adb_path, 'start-server'])
            await asyncio.sleep(20)
            await ctx.send("Сервер adb успешно перезапущен.")
            await devices(ctx)
        except Exception as e:
            await ctx.send(f"Ошибка при перезагрузке ADB: {e}")

@bot.command()
async def matrix(ctx):
    capture_screenshot()
    imageworks.add_grid_to_screenshot('screenshot.png', (25, 15))
    with open('coords.png', 'rb') as f:
        image = discord.File(f, filename='coords.png')
        await ctx.send(file=image)

def click_on_coordinate(coord_number):
    center_x, center_y = globals()[f'coord_{coord_number}']
    tap_random((center_x, center_y))

@bot.command()
async def tap(ctx, square_number):
    square_number = int(square_number)
    if f'coord_{square_number}' in globals():
        click_on_coordinate(square_number)
        await ctx.send('Клик по квадрату выполнен')
    else:
        await ctx.send('Неверный номер квадрата')

def get_voice_channel_id():
    config_file = 'config.txt'
    voicechannel = None

    with open(config_file, 'r') as file:
        for line in file:
            if 'voicechannel' in line:
                voicechannel = line.split('=')[1].strip()

    return int(voicechannel) if voicechannel else None

def read_channels_from_config():
    config_file = 'config.txt'
    channels = []

    with open(config_file, 'r') as file:
        for line in file:
            if 'channels' in line:
                channels = line.split('=')[1].strip().split(',')
    return channels

async def send_message_to_channels(bot, channels, file):
    for channel_id in channels:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(file=file)

@bot.event
async def on_ready():
    capture_screenshot()
    print(f'Погнали!')

    voicechannel = get_voice_channel_id()

    if voicechannel is not None:
        voice_channel = bot.get_channel(voicechannel)
        vc = None

        if vc is None:
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

@bot.command()
async def devices(ctx):
    devices = get_adb_devices()
    if devices is not None:
        await ctx.send('\n'.join(devices))

def get_adb_devices():
    try:
        devices = []
        output = subprocess.check_output([r'platform-tools/adb.exe', 'devices']).decode('utf-8').strip().split('\n')

        for line in output[1:]:
            if '\tdevice' in line:
                device = line.split('\t')[0]
                devices.append(device)
        return devices
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при выполнении команды: {e}')
    except Exception as e:
        print(f'Ошибка: {e}')

def get_system_stats():
    cpu_load = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    active_windows = []

    for window in gw.getAllTitles():
        if "BlueStacks" in window:
            active_windows.append(window)
            windows_column = '\n'.join(active_windows)

    return cpu_load, memory_usage, windows_column

@bot.command()
async def starteve(ctx):
    adb_path = r'C:/platform-tools/adb.exe'
    command = f'{adb_path} shell am start -n com.netease.eve.en/com.netease.ntunisdk.base.deeplink.UniDeepLinkActivity'
    try:
        subprocess.run(command, shell=True, check=True)
        print("Приложение успешно запущено")
    except subprocess.CalledProcessError:
        print("Ошибка при запуске приложения")
    await ctx.send("Запускаю игровой клиент")

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
    developer_id = 663106596825595917
    user = ctx.author
    await ctx.send(f"Перезагрузка скрипта, все функции отключены. Пользователь {user.name} выполнил эту команду.")
    developer = await bot.fetch_user(developer_id)
    await developer.send(f"Команда перезапуска была выполнена пользователем {user.name}")
    python = sys.executable
    os.execl(python, python, *sys.argv)

@bot.command()
async def press(ctx, key: str):
    keyboard.send(key)
    await ctx.send(f'pressed {key}')

@bot.command()
async def screen(ctx):
    try:
        subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
        subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screen.png'], stdout=subprocess.DEVNULL)
        image_path = 'screen.png'
        img = cv2.imread(image_path)
        resized_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        cv2.imwrite('screenmin.png', resized_img)
        with open('screenmin.png', 'rb') as f:
            image = discord.File(f, filename='screenmin.png')
        await ctx.send(file=image)
    except Exception as e:
        await ctx.send(f"Произошла ошибка: {e}")

@bot.command()
async def play(ctx):
    if not ctx.author.voice:
        await ctx.send("Вы не находитесь в голосовом канале.")
        return
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client
    if not voice_client:
        voice_client = await voice_channel.connect()
    voice_client.play(discord.FFmpegPCMAudio('grid.mp3'), after=lambda e: print('done', e))

####################################################BOT AI

@bot.command()
async def zoom(ctx):
    await adb.zoom()

@bot.command()
async def core(ctx):
    await adb.core()
    await ctx.send("Нажимаю на ядро")

@bot.command()
async def openlocal(ctx):
    await adb.openlocal()

@bot.command()
async def openover(ctx):
    await adb.openover()

@bot.command()
async def closeover(ctx):
    await adb.closeover()
    await ctx.send("Закрываю овервью")

@bot.command()
async def pilot(ctx):
    await adb.pilot()
    await ctx.send("Устанавливаю автопилот")

@bot.command()
async def login(ctx):
    await adb.login()
    await ctx.send("Логинюсь")

@bot.command()
async def dock(ctx):
    await adb.dock()
    await ctx.send("Кликаю по букмарке")

@bot.command()
async def undock(ctx):
    await adb.undock()
    await ctx.send("Андокаюсь")

@bot.command() #нажать на скилл импланта
async def roll(ctx):
    await adb.nanocore()
    await ctx.send("Пиздабол")

@bot.command() #Остановить все циклы и отключить от voice бота
async def stop(ctx):
    global looping
    looping = False
    #await ctx.send("Отключаюсь")
    #await speak(ctx, message="Отключаюсь!")

@bot.command() #Основной бот автоядра
async def starter(ctx):
    global current_status
    global looping
    looping = True
    capture_screenshot()
    cv2.imwrite(previous_file, imageworks.process_image('screenshot.png'))
    while looping:
        await asyncio.sleep(0.1)
        #await ctx.send("Поехали")
        try:
            while looping:
                await asyncio.sleep(0.5)
                capture_screenshot()
                result = await imageworks.check_enemies()
                if result:
                    tap_random(click_coords)
                    await ctx.send("Обнаружена угроза!")
                    with open('screenshot.png', 'rb') as f:
                        picture = discord.File(f)
                        await ctx.send(file=picture)
                        await dock_detector() #инициализация проверки врагов в доке с условием выхода
                else:
                    current_status = 'Пытаюсь крабить, все тихо'
                    await imageworks.main_processor() #процесс автолока, проверки щитов у цели
        except Exception as e:
            print("Произошла ошибка:")
            traceback.print_exc()
            with open("error_log.txt", "a") as f:
                f.write("Произошла ошибка:\n")
                f.write(traceback.format_exc())
        await asyncio.sleep(1)
    if not looping:
        current_status = 'Ожидаю команду'

 #инициализация бесконечного цикла проверки врагов в доке с условием выхода
async def dock_detector():
    global current_status
    global looping
    looping = True
    while looping:
        if not looping:
            current_status = 'Ожидаю команду'
            break
        current_status = 'Прячусь в доке'
        #print("инициализация перезапуска")
        await asyncio.sleep(20)
        capture_screenshot()
        result = await imageworks.check_enemies()
        if result:
            print("в системе враги, жду 20 секунд")
        else:
            await runner()
            break

@bot.command() #Инициализация выхода из дока и подготовка к старту
async def runner(ctx):
    await adb.undock()
    await asyncio.sleep(16)
    result = await imageworks.check_autopilot()
    if result:
        await adb.pilot()
    await asyncio.sleep(1)
    await adb.core()
    await asyncio.sleep(1)

############################################################## мониторинг, локалбот

def capture_screenshot():
    subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
    subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screenshot.png'],
                   stdout=subprocess.DEVNULL)

@bot.command() #Запуск мониторинга локалбота
async def start(ctx):
    channels = read_channels_from_config()
    global current_status
    global looping
    looping = True
    while looping:
        #start_time = time.time()
        try:
            connected = adb.check_device_connection(device_id)
            app_running = adb.check_app_running(device_id)
            if not connected:
                await ctx.send('Ошибка подключения к эмулятору')
                break
            elif not app_running:
                await ctx.send('Ошибка подключения к игровому клиенту')
                break
            else:
                capture_screenshot()
                await asyncio.sleep(0.5)
                image = cv2.imread('screenshot.png')
                img1 = image[crop_coordss[0][0]:crop_coordss[0][1], crop_coordss[0][2]:crop_coordss[0][3]]
                img2 = image[crop_coordss[1][0]:crop_coordss[1][1], crop_coordss[1][2]:crop_coordss[1][3]]
                img3 = image[crop_coordss[2][0]:crop_coordss[2][1], crop_coordss[2][2]:crop_coordss[2][3]]
                imgh = cv2.hconcat([img2, img1])
                dsize = (618, 423)
                imgh = cv2.resize(imgh, dsize)
                result = cv2.vconcat([img3, imgh])
                cv2.imwrite(local_file, result)
                imageworks.add_watermark(local_file)
                result = await imageworks.check_enemies()
                if result:
                    current_status = 'Угроза безопасности'
                    await asyncio.sleep(0.5)
                    grid_result = await grid(ctx)
                    if grid_result:
                        for channel_id in channels:
                            channel = bot.get_channel(int(channel_id))
                            if channel:
                                try:
                                    await channel.send(file=discord.File(local_file))
                                except Exception as e:
                                    print(f"Ошибка при отправке изображения в канал Discord: {e}")
                        break
                else:
                    #end_time = time.time()
                    #execution_time = end_time - start_time
                    #print(f"Время выполнения функции: {execution_time} секунд")
                    current_status = 'Угроз не обнаружено'
                    grid_result = False
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
        finally:
            if not looping:
                current_status = 'Ожидаю команду'

#Обработка грида овервью
async def grid(ctx):
    try:
        channels = read_channels_from_config()
        img = cv2.imread('local.png')
        if img is None:
            print("Ошибка при чтении изображения")
            return

        if any(var is None for var in [crop_dy1, crop_dy2, crop_dx1, crop_dx2]):
            print("Ошибка: одна или несколько переменных crop_* не определена")
            return
        img_cropped1 = img[crop_dy1:crop_dy2, crop_dx1:crop_dx2]
        cv2.imwrite('grid.png', img_cropped1)
        img_cropped2 = img[crop_cy1:crop_cy2, crop_cx1:crop_cx2]
        cv2.imwrite('name.png', img_cropped2)
        img2 = cv2.imread('grid.png')
        img3 = cv2.imread('name.png')
        if img2 is not None and img3 is not None:
            text = pytesseract.image_to_string(img2, config='--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"', output_type='string')
            if text:
                print("Обнаружен террорист: ", text)
                cv2.imwrite('ocrresult.png', img2)
                for channel_id in channels:
                    channel = bot.get_channel(int(channel_id))
                    if channel:
                        try:
                            await channel.send(file=discord.File(local_file))
                            await channel.send(f'{text}')
                        except Exception as e:
                            print(f"Ошибка при отправке изображения в канал Discord: {e}")
                await asyncio.sleep(0.5)
                voice_channel_id = get_voice_channel_id()
                if voice_channel_id:
                    voice_channel = bot.get_channel(voice_channel_id)
                    vc = ctx.voice_client
                    if not vc:
                        vc = await voice_channel.connect()
                    elif vc.channel != voice_channel:
                        await vc.move_to(voice_channel)
                    vc.play(discord.FFmpegPCMAudio('grid.mp3'))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Ошибка при обработке изображения в функции grid(): {e}")

@bot.command() #Текущий статус бота по глобальным флагам
async def status(ctx):
    await ctx.send(f"Текущий статус мониторинга: {current_status}")
    #await speak(ctx, message=current_status)

@bot.command() #получение комбинированного актуального изображения в дискорд канал
async def local(ctx):
    if not looping:
        await ctx.send("Нельзя получить скриншот пока не запустите цикл !start.")
    else:
        with open(local_file, 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    await asyncio.sleep(1)

@bot.command() #отладка, визуализация машинного зрения
async def showfiles(ctx):
    with open('1.png', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
    with open('2.png', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
        img1 = cv2.imread(previous_file)
        img2 = cv2.imread(current_file)
        diff = cv2.absdiff(img1, img2)
        nonzero_count = np.count_nonzero(diff)
        await ctx.send(f"Различие пикселей: {nonzero_count}")

@bot.command()
async def diff(ctx):
    img1 = cv2.imread(previous_file)
    img2 = cv2.imread(current_file)
    diff = cv2.absdiff(img1, img2)
    nonzero_count = np.count_nonzero(diff)
    await ctx.send(f"Различие пикселей: {nonzero_count}, порог:175")

@bot.command() #починить изображения способом подмены
async def repairimages(ctx):
    target_image = 'screenshot.png'
    new_image = 'screen.png'

    if os.path.exists(target_image):
        os.remove(target_image)
        os.rename(new_image, target_image)

    target_image = '1.png'
    new_image = '2.png'

    if os.path.exists(target_image):
        os.remove(target_image)
        os.rename(new_image, target_image)
        await ctx.send("починил")

##########################################################################################################TTS Fnc

@bot.command() #to say something on the Discord channel
async def speak(ctx, *, message):
    if ctx.author.voice is None:
        await ctx.send("Вы должны находиться в голосовом канале, чтобы использовать эту команду.")
        return
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Настройка скорости речи (по умолчанию 200)
    engine.setProperty('volume', 1)  # Настройка громкости речи (от 0 до 1)
    voices = engine.getProperty('voices')
    russian_voice = None
    for voice in voices:
        if "Russian" in voice.name:
            russian_voice = voice
            break
    if russian_voice:
        engine.setProperty('voice', russian_voice.id)
    filename = 'voice_message.wav'
    engine.save_to_file(message, filename)
    engine.runAndWait()
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        voice_client = await voice_channel.connect()
    else:
        voice_client = ctx.voice_client
    voice_client.play(discord.FFmpegPCMAudio(filename))
    while voice_client.is_playing():
        await asyncio.sleep(1)

##################################################################################### Autocrab

@bot.command()
async def craber(ctx):
    global current_status
    global looping
    looping = True
    capture_screenshot()
    cv2.imwrite(previous_file, imageworks.process_image('screenshot.png'))
    if not looping:
        current_status = 'Ожидаю команду'
    while looping:
        capture_screenshot()
        location = imageworks.determine_location("screenshot.png")
        if location == "pos" or location == "dock":
            result = await imageworks.check_enemies()
            if result:
                await ctx.send("Обнаружена угроза!")
                with open('screenshot.png', 'rb') as f:
                    picture = discord.File(f)
                    await ctx.send(file=picture)
                current_status = 'В системе враги, ожидаю 60 секунд'
                print("В системе враги, ожидаю 90 секунд")
                await asyncio.sleep(90)
            else:
                await runner(ctx)
                current_status = 'Клацаю клешнями'
                await imageworks.autocraber()
        else:
            if location == "space":
                result = await imageworks.check_autopilot()
                if result:
                    await adb.pilot()
                    await asyncio.sleep(0.1)
                result = await imageworks.check_open_over()
                if not result:
                    await adb.openover()
            capture_screenshot()
            await asyncio.sleep(1)
            result = await imageworks.check_enemies()
            if result:
                await ctx.send("Обнаружена угроза!")
                with open('screenshot.png', 'rb') as f:
                    picture = discord.File(f)
                    await ctx.send(file=picture)
                current_status = 'В системе враги, ожидаю 90 секунд'
                print("В системе враги, докаюсь")
                tap_random(click_coords)
                await asyncio.sleep(90)
            else:
                current_status = 'Краблю'
                await imageworks.autocraber()

@bot.command()
async def test(ctx):
    result = imageworks.pixcolor()
    await ctx.send(result)


'''
############################################################## trade

number_coordinates = {
    "0": (777, 463),
    "1": (663, 267),
    "2": (777, 269),
    "3": (893, 267),
    "4": (667, 332),
    "5": (778, 332),
    "6": (891, 335),
    "7": (662, 400),
    "8": (778, 397),
    "9": (890, 398),
}

def click_number(number):
    for digit in str(number):
        x, y = number_coordinates[digit]
        adb.tap_cortage(x, y)

def extract():
    crop_x1, crop_y1, crop_x2, crop_y2 = 564, 245, 702, 267
    screenshot = cv2.imread('screenshot.png')
    cropped_image = screenshot[crop_y1:crop_y2, crop_x1:crop_x2]
    gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    price_text = pytesseract.image_to_string(gray_image, config='--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"', output_type='string')
    price_text = price_text.replace('.', '').replace(',', '')
    price_text = price_text.split('.')[0]
    cv2.imwrite("price.png", gray_image)

    return price_text

def crop():
    crop_x1, crop_y1, crop_x2, crop_y2 = 120, 91, 541, 176
    screenshot = cv2.imread('screenshot.png')
    cropped_image = screenshot[crop_y1:crop_y2, crop_x1:crop_x2]
    cv2.imwrite("Name.png", cropped_image)

async def processorder(ctx):
    close = (856, 66)
    buyclick = (48, 232)
    buy = (793, 468)
    tapcalculate = (540, 217)
    pcs = (589, 284)
    order = (480, 468)####################################################################
    await asyncio.sleep(4)
    capture_screenshot()
    await asyncio.sleep(2)
    crop()
    await asyncio.sleep(3)
    price_text = extract()
    print(f"price_text: {price_text}")
    price_number = float(price_text.replace(',', '.').split('.')[0])
    seventy_percent = int(price_number * 0.7)
    margin = int(price_number * 0.15)
    with open('Name.png', 'rb') as f:
        picture = discord.File(f)
    await ctx.send(file=picture)
    await ctx.send(f"Текущая цена: {price_text}")
    await ctx.send(f"Устанавливаемая цена: {seventy_percent}")
    await ctx.send(f"Предполагаемая маржа: {margin}")
    tap_random(buyclick)
    await asyncio.sleep(2)
    tap_random(buy)
    await asyncio.sleep(1)
    tap_random(tapcalculate)
    await asyncio.sleep(0.5)
    click_number(seventy_percent)
    await asyncio.sleep(1)
    tap_random(pcs)
    click_number(1)
    tap_random(order)
    await asyncio.sleep(1)
    tap_random(close)


@bot.command()
async def trade(ctx):
    marketclick = (137, 88)
    favorites = (104, 517)
    item_01 = (313, 127)
    item_02 = (493, 121)
    item_03 = (683, 131)
    item_04 = (866, 128)
    item_05 = (310, 270)
    item_06 = (496, 269)
    item_07 = (682, 267)
    item_08 = (863, 269)
    tap_random(marketclick)
    await asyncio.sleep(4)
    tap_random(favorites)
    await asyncio.sleep(3)
    tap_random(item_01)             ############################## Отсчетная точка
    await processorder(ctx)
'''

if __name__ == "__main__":
    with open(config_file, 'r') as file:
        for line in file:
            if 'token' in line:
                token = line.split('=')[1].strip()

    if token is not None:
        pass
    else:
        print("Значение token не найдено.")
    bot.run(token)

