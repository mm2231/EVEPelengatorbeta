import asyncio
import os
import subprocess
import sys
import traceback
import cv2
import discord
import keyboard
import numpy as np
import pygame
import pytesseract
import pyttsx3
from discord.ext import commands
from pyttsx3 import engine
import ffmpeg
import adb
import imageworks
from adb import capture_screenshot, focus, tap_random, unload, undock, click_coords3, pilot, dock, openover, swipe, \
    click_coords

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
current_status = 'Бот в режиме ожидания'
looping = False
mining = False
voice_client = None
voicechannel = None #1155398920936108122 zlata 1143557824429961352 my
device_id = None
token = None

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
devices = output.strip().split("\n")[1:]'''

'''def select_device(devices):
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

def get_voice_channel_id():
    config_file = 'config.txt'
    voicechannel = None

    with open(config_file, 'r') as file:
        for line in file:
            if 'voicechannel' in line:
                voicechannel = line.split('=')[1].strip()

    return int(voicechannel) if voicechannel else None

@bot.event
async def on_ready():
    print(f'Ready to go')

    voicechannel = get_voice_channel_id()

    if voicechannel is not None:
        voice_channel = bot.get_channel(voicechannel)
        vc = voice_client

        if not vc:
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

@bot.command()
async def devices(ctx):
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        devices_output = result.stdout.strip()
        await ctx.send(f"Список устройств ADB:\n{devices_output}")
    except Exception as e:
        await ctx.send(f"Ошибка при получении списка устройств ADB: {e}")

@bot.command()
async def starteve(ctx):
    adb_path = r'C:/platform-tools/adb.exe'
    command = f'{adb_path} shell am start -n com.netease.eve.en/com.netease.ntunisdk.base.deeplink.UniDeepLinkActivity'
    try:
        subprocess.run(command, shell=True, check=True)
        print("The application has been successfully launched")
    except subprocess.CalledProcessError:
        print("Error when launching the application")
    await ctx.send("Launching the game client")

@bot.command()
async def closeeve(ctx):
    adb_path = "C:/platform-tools/adb.exe"
    package_name = "com.netease.eve.en"
    command = f'{adb_path} shell am force-stop {package_name}'
    try:
        subprocess.run(command, shell=True, check=True)
        await ctx.send("Application closed successfully")
    except subprocess.CalledProcessError:
        await ctx.send("Error when closing the application")

@bot.command()
async def restart(ctx):
    await ctx.send("Restarting the script, all functions are disabled")
    subprocess.Popen([sys.executable, "restart_script.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    await bot.close()

@bot.command()
async def press(ctx, key: str):
    keyboard.send(key)
    await ctx.send(f'pressed {key}')

@bot.command()
async def screen(ctx):
    subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
    subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screen.png'],
                   stdout=subprocess.DEVNULL)
    await asyncio.sleep(0.5)
    image_path = 'screen.png'
    img = cv2.imread(image_path)
    resized_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv2.imwrite('screenmin.png', resized_img)

    with open('screenmin.png', 'rb') as f:
        image = discord.File(f, filename='screenmin.png')
        await ctx.send(file=image)

####################################################BOT

@bot.command()
async def zoom(ctx):
    await adb.zoom()
    await ctx.send("Зум камеры")

@bot.command()
async def core(ctx):
    await adb.core()
    await ctx.send("Нажимаю на ядро")

@bot.command()
async def openlocal(ctx):
    await adb.openlocal()
    await ctx.send("Нажимаю на локал")

@bot.command()
async def openover(ctx):
    await adb.openover()
    await ctx.send("Открываю овервью")

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

@bot.command()
async def stop(ctx):
    global looping
    looping = False
    await ctx.send("Отключаюсь")
    await speak(ctx, message="Отключаюсь!")
    voice_client = ctx.voice_client
    if voice_client is None:
        return
    await voice_client.disconnect()

@bot.command()
async def starter(ctx):
    global looping
    looping = True
    while looping:
        await asyncio.sleep(0.1)
        #await speak(ctx, message="Погнали!")
        await ctx.send("Поехали")
        try:
            capture_screenshot()    # Здесь начинается магия с подменой 1.png
            cv2.imwrite(previous_file, imageworks.process_image('screenshot.png'))
            while looping:
                await asyncio.sleep(0.1)
                capture_screenshot()
                cv2.imwrite(current_file, imageworks.process_image('screenshot.png'))
                img1 = cv2.imread(previous_file)
                img2 = cv2.imread(current_file)
                diff = cv2.absdiff(img1, img2)
                print(np.count_nonzero(diff))
                if np.count_nonzero(diff) >= 175:
                    print(f'Alarm!')
                    tap_random(click_coords)
                    #await speaker(ctx, message="Обнаружена угроза. Корабль направлен в док!")
                    await ctx.send("Тревога!")
                    await ctx.send(np.count_nonzero(diff))
                    cv2.imwrite('3.png', diff)
                    with open('3.png', 'rb') as f:
                        picture = discord.File(f)
                        await ctx.send(file=picture)
                    pygame.mixer.init()
                    pygame.mixer.music.load("diff.mp3")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        with open('screenshot.png', 'rb') as f:
                            picture = discord.File(f)
                            await ctx.send(file=picture)
                        continue
                    return
                else:
                    #print('Все в порядке')
                    #await imageworks.check_open_over() #проверка на овервью ########################
                    #keywords = "small,medium,large"
                    #await imageworks.find(keywords)
                    #await asyncio.sleep(1)
                    #keywords1 = "Wapr,warp,arp,war"
                    #await imageworks.find(keywords1)
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
                        await imageworks.processlock()
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
                            image_path = "screenshot.png" #Проверка на окно ошибки сеток
                            img = cv2.imread(image_path)
                            x = 641  # Координата x
                            y = 186  # Координата y
                            b, g, r = img[y, x]  # Получаем значения синего, зеленого и красного цветов пикселя
                            r_min = 130  # Минимальное значение R
                            g_max = 170  # Максимальное значение G
                            b_max = 161  # Максимальное значение B
                            print("Значения RGB пикселя:", r, g, b)
                            if r > r_min and g < g_max and b < b_max:
                                closestasis = (635, 180)
                                tap_random(closestasis)
        except Exception as e:
            print("Произошла ошибка:")
            traceback.print_exc()
            with open("error_log.txt", "a") as f:
                f.write("Произошла ошибка:\n")
                f.write(traceback.format_exc())
        await asyncio.sleep(1)

############################################################## мониторинг, локалбот

def capture_screenshot():
    subprocess.run([adb_path, '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
    subprocess.run([adb_path, '-s', device_id, 'pull', '/sdcard/screenshot.png', './screenshot.png'],
                   stdout=subprocess.DEVNULL)

@bot.command()
async def start(ctx):
    await speak(ctx, message="Запускаю мониторинг!")
    global current_status
    global looping
    print('Запускаю цикл скринов')
    looping = True
    while looping:
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
        result = await imageworks.check_enemies()
        if result:
            current_status = 'запущен цикл, угроза безопасности в системе'
            #print("в системе враги")
            await asyncio.sleep(1.5)
            grid_result = await grid(ctx)
            if grid_result:
                await ctx.send(file=discord.File('local.png'))
                break
        else:
            current_status = 'запущен цикл, угроз не обнаружено'
            grid_result = False


async def grid(ctx):
    img = cv2.imread('local.png')
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
            await ctx.send(file=discord.File('local.png'))
            await asyncio.sleep(0.5)
            await ctx.send(f'{text}')
            voice_channel = bot.get_channel(voicechannel)
            vc = ctx.voice_client
            if not vc:
                vc = await voice_channel.connect()
            elif vc.channel != voice_channel:
                await vc.move_to(voice_channel)
            await speak(ctx, message="Внимание! Обнаружена угроза!")
            await speak(ctx, message=text)
        await asyncio.sleep(1)

def play_text(ctx, vc, file):
     vc.play(discord.FFmpegPCMAudio(file), after=lambda e: print('done', e))

@bot.command()
async def status(ctx):
    await ctx.send(current_status)
    #await speak(ctx, message=current_status)

@bot.command()
async def local(ctx):
    if not looping:
        await ctx.send("Нельзя получить скриншот пока не запустите цикл !start.")
    else:
        with open(local_file, 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    await asyncio.sleep(1)

@bot.command()
async def showfiles(ctx): #отладка, визуализация машинного зрения
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
async def repairimages(ctx): #починить изображения
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

@bot.command() #text to speach fnc, save the file and send it to discord channel
async def tts(ctx, text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Настройка скорости речи (по умолчанию 200)
    engine.setProperty('volume', 1)  # Настройка громкости речи (от 0 до 1)
    voices = engine.getProperty('voices')
    russian_voice_index = 0  # Индекс русского голоса
    engine.setProperty('voice', voices[russian_voice_index].id)
    filename = 'voice_message.mp3'
    engine.save_to_file(text, filename)
    engine.runAndWait()
    with open(filename, 'rb') as file:
        await ctx.send(file=discord.File(file, filename))

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


##MTE0MjQxMDg2OTMyMjU2MzU5NA.GrWfeF.EwM5X7ZimEonI01IimlOtmO4Zu1jzHGbfluvDc ZLATA
##MTA5NDk0NzQzMzczMTA4NDM4OA.Gd6cRT.gx0rSe4vo8Q9dA4nMkpDq144XrWWyeTsqmslP4 MY
##MTE1NTQxMzA3NjEzNzQ5NjU4Ng.GfOopR.WO9pUDoVd4JSV-lIzrHc0FedE2Fa9YCmnzEPe0 zlata3