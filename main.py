import pyttsx3      # Синтез речи
import datetime     # Работа со временем
import speech_recognition as sr     # Распознавание речи online
from vosk import Model, KaldiRecognizer     # Распознавание речи offline
import wave     # Создание и чтение аудиофайлов формата .wav
import os       # Работа с файловой системой
import json     # Работа с данными в формате JSON
import wikipediaapi     # Доступ к API Википедии
import webbrowser       # Открытие вкладок браузера
import traceback        # Формирование информации об исключениях
from googletrans import Translator      # Доступ к API Google Translate
import subprocess       # Запуск новых процессов
import random       # Генератор случайных чисел
from pathlib import Path        # Работа с путями файловой системы
import requests     # Отправка HTTP-запросов и получение ответов от Web-серверов
import os
import tkinter as tk
import re
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log
import asyncio
from functools import partial
import logging
logging.basicConfig(level=logging.DEBUG)

# Класс ассистента
class Bot:
    def __init__(self):
        self.bot_name_ru = "Макс"
        self.bot_name_en = "Max"
        self.city = "Москва"
        self.language = "ru"

# Класс для мультиязычности
class bot_translate:
    with open("translations.json", "r", encoding="UTF-8") as file:  # Подключение к файлу с переводами
        translations = json.load(file)

# Класс для мультиязычности
class BotTranslate:
    def __init__(self):
        with open("translations.json", "r", encoding="UTF-8") as file:
            self.translations = json.load(file)

    def get(self, text: str):
        if text in self.translations:
            return self.translations[text][trex.language]
        else:
            print(f"Для фразы: {text} нет перевода.")
            return text


class AssistantUI(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [("q", "quit", "Выход")]

    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance

    # В классе AssistantUI замените метод compose на этот код
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            f"[b][#3498db]Голосовой помощник[/] [u]{self.bot.bot_name_ru}[/][/]",
            id="title",
            classes="box"
        )
        yield Static(
            "[#2ecc71]▸ Статус:[/]",
            id="status-label",
            classes="box"
        )
        yield Static(
            "[#e67e22]Ожидание активации...[/]",
            id="status",
            classes="box"
        )
        yield Static(
            "[#9b59b6]▸ История команд:[/]",
            id="history-label",
            classes="box"
        )
        yield Log(highlight=True, classes="logbox")  # Убрали несуществующий параметр markup
        yield Footer()

    def update_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def add_log(self, message: str) -> None:
        self.query_one(Log).write_line(message)

    async def on_mount(self) -> None:
        self.run_worker(self.process_commands())

    async def process_commands(self):
        """
        Основной цикл обработки команд голосового помощника.
        Работает в фоновом режиме, ожидая активации и выполнения команд.
        """
        while True:  # Бесконечный цикл для постоянного ожидания команд
            try:
                # 1. Получение голосовой команды
                query = await self.run_async(record).lower()  # Асинхронный вызов функции записи

                # 2. Проверка активации помощника
                activation_pattern = re.compile(
                    rf'^\s*{re.escape(self.bot.bot_name_ru.lower())}\b[\s,!;]*',
                    re.IGNORECASE
                )
                match = activation_pattern.match(query)

                # Если команда не содержит активации, игнорируем её
                if not match:
                    self.add_log(f"[bold red]Игнор:[/] {query}")
                    await asyncio.sleep(0.1)  # Короткая пауза перед следующей итерацией
                    continue

                # 3. Извлечение команды после активации
                command = query[match.end():].strip()

                # Если команда пустая, просто отвечаем
                if not command:
                    await speak(self.bot, "Да, слушаю вас!")
                    self.add_log("[bold blue]Активация:[/] Получена пустая команда")
                    continue

                # 4. Логирование команды
                self.add_log(f"[bold green]Команда:[/] {command}")

                # 5. Обработка команды
                try:
                    if any(x in command for x in ["википедия", "wikipedia"]):
                        self.update_status("Поиск в Википедии...")
                        search_wiki(command)
                    elif any(x in command for x in ["гугл", "google"]):
                        self.update_status("Поиск в Google...")
                        search_google(command)
                    elif any(x in command for x in ["яндекс", "yandex"]):
                        self.update_status("Поиск в Яндексе...")
                        search_yandex(command)
                    elif any(x in command for x in ["ютуб", "youtube"]):
                        self.update_status("Поиск на YouTube...")
                        search_youtube(command)
                    elif any(x in command for x in ["рутуб", "rutube"]):
                        self.update_status("Поиск на RuTube...")
                        search_rutube(command)
                    elif any(x in command for x in ["открой", "open"]):
                        self.update_status("Открытие сайта...")
                        search_website(command)
                    elif any(x in command for x in ["переведи", "перевод", "translate"]):
                        self.update_status("Перевод...")
                        translate(command)
                    elif any(x in command for x in ["время", "time"]):
                        self.update_status("Определение времени...")
                        time()
                    elif any(x in command for x in ["запуск", "запусти", "start"]):
                        self.update_status("Запуск приложения...")
                        start_app(command)
                    elif any(x in command for x in ["музыка", "музыку", "music"]):
                        self.update_status("Запуск музыки...")
                        play_music()

                    # Возвращаем статус "Готов к работе" после выполнения команды
                    self.update_status("Готов к работе")

                except Exception as e:
                    # Логируем ошибку выполнения команды
                    self.add_log(f"[bold red]Ошибка выполнения команды:[/] {str(e)}")
                    self.update_status("Ошибка выполнения")
                    traceback.print_exc()

                # 6. Короткая пауза перед следующей итерацией
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                # Корректное завершение при закрытии приложения
                self.add_log("[bold yellow]Завершение работы помощника...[/]")
                break

            except Exception as e:
                # Логируем критические ошибки
                self.add_log(f"[bold red]Критическая ошибка:[/] {str(e)}")
                traceback.print_exc()
                await asyncio.sleep(1)  # Защита от бесконечного цикла ошибок

def record():
    query = ""
    with microphone:
        recognizer.adjust_for_ambient_noise(microphone, duration=1)  # Регулирование уровня окружающего шума
        try:
            print(f"{trex.bot_name_ru} слушает...")
            rec_audio = recognizer.listen(microphone, 5, 5)     # Запись голоса с микрофона
            with open("recorded_speech.wav", "wb") as file:     # Сохранение аудио в файл
                file.write(rec_audio.get_wav_data())
            query = online_recognition()    # Запуск online-распознавания
        except sr.WaitTimeoutError:
            speak(trex, translator.get(""))
        except Exception as e:
            print(f"Ошибка при записи речи: {e}")
            speak(trex, "Произошла ошибка при записи речи. Пожалуйста, повторите запрос.")
    return query

# Воспроизведение речи ассистента
async def speak(my_bot, text):
    print(f"{my_bot.bot_name_ru} говорит: {text}.")
    engine.say(text)
    await asyncio.to_thread(engine.runAndWait)

# Приветственное сообщение при запуске программы
async def greetings():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 6:
        await speak(trex, f"Доброй ночи! Я - {trex.bot_name_ru}, ваш голосовой помощник.")
    elif 6 <= hour < 12:
        await speak(trex, f"Доброе утро! Я - {trex.bot_name_ru}, ваш голосовой помощник.")
    elif 12 <= hour < 18:
        await speak(trex, f"Добрый день! Я - {trex.bot_name_ru}, ваш голосовой помощник.")
    else:
        await speak(trex, f"Добрый вечер! Я - {trex.bot_name_ru}, ваш голосовой помощник.")

# Online-распознавание речи
def online_recognition():
    query = ""
    try:
        rec_audio = sr.WavFile("recorded_speech.wav")   # Чтение аудиофайла с речью
        with rec_audio as audio:
            content = recognizer.record(audio)
        print(f"{trex.bot_name_ru} распознает речь...")
        query = recognizer.recognize_google(content, language="ru-RU").lower()
    except sr.UnknownValueError:
        pass
    except sr.RequestError:  # При недоступности Интернета - переключение на offline-распознавание
        print(f"{trex.bot_name_ru} не смог подключиться к Интернету. Попытка offline-распознавания...")
        query = offline_recognition()
    return query

# Offline-распознавание речи
def offline_recognition():
    vosk_model = "vosk-model-ru-0.42"   # Используемая модель Vosk
    query = ""
    try:
        if not os.path.exists(f"models/{vosk_model}"):  # Проверка наличия модели на нужном языке в каталоге приложения
            print(f"ВНИМАНИЕ: Для offline-распознавания необходимо загрузить языковую модель \"{vosk_model}\" с сайта https://alphacephei.com/vosk/models и распаковать в директорию проекта.")
            exit(1)
        audio_file = wave.open("recorded_speech.wav", "rb")
        model = Model(f"models/{vosk_model}")
        offline_recognizer = KaldiRecognizer(model, audio_file.getframerate())
        audio = audio_file.readframes(audio_file.getnframes())
        if len(audio) > 0:
            if offline_recognizer.AcceptWaveform(audio):
                query = offline_recognizer.Result()
                query = json.loads(query)
                query = query["text"]
    except:
        speak(trex, "Извините, я не смог распознать речь. Пожалуйста, повторите запрос")
    return query

# Поиск по Википедии
def search_wiki(query):
    speak(trex, "Произвожу поиск по Википедии")
    wiki = wikipediaapi.Wikipedia(f"{trex.bot_name_en} ({trex.bot_name_en}@selectel.ru)", "ru")
    query = query.replace("википедия ", "")     # Удаляем ненужные слова запроса
    query = query.replace("википедии ", "")
    query = query.replace("wikipedia ", "")
    wiki_page = wiki.page(query)
    try:
        if wiki_page.exists():
            speak(trex, f"Вот что мне удалось найти в Википедии по запросу \"{query}\"")
            webbrowser.open(wiki_page.fullurl)  # Открытие ссылки в браузере
            result = wiki_page.summary.split(".")[:2]   # Выборка двух первых предложений
            speak(trex, result)
        else:
            speak(trex, f"К сожалению, я не смог ничего найти на Википедии по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск по Википедии\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return

# Поиск в Google
def search_google(query):
    speak(trex, "Произвожу поиск в Google")
    query = query.replace("гугл ", "")  # Удаление ненужных слов в запросе
    query = query.replace("гугле ", "")
    query = query.replace("google ", "")
    try:
        URI = "https://google.com/search?q=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти в Google по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск в Google\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return

# Поиск в Яндексе
def search_yandex(query):
    speak(trex, "Произвожу поиск в Яндексе")
    query = query.replace("яндекс ", "")    # Удаление ненужных слов в запросе
    query = query.replace("yandex ", "")
    try:
        URI = "https://ya.ru/search?text=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти в Яндексе по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск в Яндексе\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return

# Поиск по YouTube
def search_youtube(query):
    speak(trex, "Произвожу поиск на YouTube")
    query = query.replace("ютуб ", "")  # Удаление ненужных слов в запросе
    query = query.replace("youtube ", "")
    try:
        URI = "https://www.youtube.com/results?search_query=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти на YouTube по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск на YouTube\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return

# Поиск по RuTube
def search_rutube(query):
    speak(trex, "Произвожу поиск на RuTube")
    query = query.replace("рутуб ", "") # Удаление ненужных слов в запросе
    query = query.replace("rutube ", "")
    try:
        URI = "https://rutube.ru/search/?query=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти на RuTube по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск на RuTube\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return

# Открытие веб-сайта
def search_website(query):
    query = query.replace("открой ", "")    # Удаление ненужных слов
    query = query.replace("open ", "")
    speak(trex, f"Произвожу поиск сайта \"{query}\"")
    try:
        URI = "https://www." + query
        webbrowser.open(URI)
        speak(trex, f"Открываю \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Открыть website\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return

# Переводчик
from googletrans import Translator
from deep_translator import GoogleTranslator


def translate(query):
    if "с английского" in query:
        lang_src = "en"
        lang_dest = "ru"
    elif "на английский" in query:
        lang_src = "ru"
        lang_dest = "en"
    else:
        speak(trex, "Извините, поддерживается только перевод с английского на русский и наоборот")
        return

    query = query.replace("переведи с английского ", "").replace("переведи на английский ", "")

    try:
        translator = GoogleTranslator(source=lang_src, target=lang_dest)
        translated_text = translator.translate(query)
        speak(trex, translated_text)
    except Exception as e:
        speak(trex, "Произошла ошибка работы модуля \"Переводчик\". Подробности ошибки выведены в терминал")
        traceback.print_exc()

# Время
def time():
    time_time = datetime.datetime.now().strftime("%H:%M:%S")
    speak(trex, f"Текущее время: {time_time}")

# Запуск приложения
def start_app(query):
    query = query.replace("запусти ", "")
    print(query)
    if ("edge" in query):
        subprocess.run("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
    elif ("калькулятор" in query):
        subprocess.run(["start calc"])
    elif ("браузер" in query):
        subprocess.run(["start chrome"])

# Запуск музыки
def play_music():
    music_dir_name = "C:\\MyMusic"
    music_dir = Path(music_dir_name)
    music = os.listdir(music_dir)
    print(f"В директории \"{music_dir}\" найдены следующие композиции: \n", music)
    music_count = len(list(music_dir.iterdir()))
    print(f"В папке {music_dir} есть {music_count} объектов")
    os.startfile(os.path.join(music_dir, music[random.randint(0, music_count-1)]))


# Инициализация и запуск приложения
if __name__ == "__main__":
    trex = Bot()

    # Инициализация движка голоса
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id if trex.language == "ru" else voices[1].id)

    # Инициализация распознавания речи
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Инициализация переводчика
    translator = BotTranslate()

    # Запуск приложения
    app = AssistantUI(trex)


    async def main():
        await app.run_async()


    asyncio.run(main())