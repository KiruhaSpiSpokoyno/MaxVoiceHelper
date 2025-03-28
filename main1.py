import pyttsx3
import datetime
import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import wave
import os
import json
import wikipediaapi
import webbrowser
import traceback
from googletrans import Translator
import subprocess
import random
from pathlib import Path
import requests
import tkinter as tk
from tkinter import scrolledtext, ttk
from PIL import Image, ImageTk
import threading


# Класс ассистента
class Bot:  # Класс с большой буквы
    def __init__(self):
        self.bot_name_ru = "Макс"
        self.bot_name_en = "Max"
        self.city = "Москва"
        self.language = "ru"
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Настройка голоса
        voices = self.engine.getProperty('voices')
        if self.language == "ru":
            self.engine.setProperty('voice', voices[0].id)
        elif self.language == "en":
            self.engine.setProperty('voice', voices[1].id)

    def record(self):
        query = ""
        with self.microphone:
            self.recognizer.adjust_for_ambient_noise(self.microphone, duration=1)
            try:
                print(f"{self.bot_name_ru} слушает...")
                rec_audio = self.recognizer.listen(self.microphone, 5, 5)
                with open("recorded_speech.wav", "wb") as file:
                    file.write(rec_audio.get_wav_data())
                query = self.online_recognition()
            except sr.WaitTimeoutError:
                self.speak("Не услышал ваш запрос")
            except Exception as e:
                print(f"Ошибка при записи речи: {e}")
                self.speak("Произошла ошибка при записи речи. Пожалуйста, повторите запрос.")
        return query

    def speak(self, text):
        print(f"{self.bot_name_ru} говорит: {text}.")
        self.engine.say(text)
        self.engine.runAndWait()

    def online_recognition(self):
        query = ""
        try:
            rec_audio = sr.WavFile("recorded_speech.wav")
            with rec_audio as audio:
                content = self.recognizer.record(audio)
            print(f"{self.bot_name_ru} распознает речь...")
            query = self.recognizer.recognize_google(content, language="ru-RU").lower()
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print(f"{self.bot_name_ru} не смог подключиться к Интернету. Попытка offline-распознавания...")
            query = self.offline_recognition()
        return query

# Приветственное сообщение при запуске программы
    def greetings(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 6:
            self.speak(f"Доброй ночи! Я - {self.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")
        elif 6 <= hour < 12:
            self.speak(f"Доброе утро! Я - {self.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")
        elif 12 <= hour < 18:
            self.speak(
                f"Приветствую! Я - {self.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")
        else:
            self.speak(
                f"Добрый вечер! Я - {self.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")


# Offline-распознавание речи
    def offline_recognition(self):
        vosk_model = "vosk-model-ru-0.42"
        query = ""
        try:
            if not os.path.exists(f"models/{vosk_model}"):
                print(f"ВНИМАНИЕ: Для offline-распознавания необходимо загрузить языковую модель \"{vosk_model}\"")
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
        except Exception as e:
            self.speak("Извините, я не смог распознать речь. Пожалуйста, повторите запрос")
            print(f"Ошибка: {e}")
        return query

    def search_wiki(self, query):
        self.speak("Произвожу поиск по Википедии")
        wiki = wikipediaapi.Wikipedia(f"{self.bot_name_en} ({self.bot_name_en}@example.com)", "ru")
        query = query.replace("википедия ", "").replace("википедии ", "").replace("wikipedia ", "")
        wiki_page = wiki.page(query)
        try:
            if wiki_page.exists():
                self.speak(f"Вот что мне удалось найти в Википедии по запросу \"{query}\"")
                webbrowser.open(wiki_page.fullurl)
                result = wiki_page.summary.split(".")[:2]
                self.speak(str(result))
            else:
                self.speak(f"К сожалению, я не смог ничего найти на Википедии по запросу \"{query}\"")
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Поиск по Википедии\"")
            traceback.print_exc()

# Поиск по Википедии
    def search_google(self, query):
        self.speak("Произвожу поиск в Google")
        query = query.replace("гугл ", "").replace("гугле ", "").replace("google ", "")
        try:
            webbrowser.open(f"https://google.com/search?q={query}")
            self.speak(f"Вот что мне удалось найти в Google по запросу \"{query}\"")
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Поиск в Google\"")
            traceback.print_exc()


    def search_yandex(self, query):
        self.speak("Произвожу поиск в Яндексе")
        query = query.replace("яндекс ", "").replace("yandex ", "")
        try:
            webbrowser.open(f"https://ya.ru/search?text={query}")
            self.speak(f"Вот что мне удалось найти в Яндексе по запросу \"{query}\"")
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Поиск в Яндексе\"")
            traceback.print_exc()


    def search_youtube(self, query):
        self.speak("Произвожу поиск на YouTube")
        query = query.replace("ютуб ", "").replace("youtube ", "")
        try:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            self.speak(f"Вот что мне удалось найти на YouTube по запросу \"{query}\"")
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Поиск на YouTube\"")
            traceback.print_exc()


    def search_rutube(self, query):
        self.speak("Произвожу поиск на RuTube")
        query = query.replace("рутуб ", "").replace("rutube ", "")
        try:
            webbrowser.open(f"https://rutube.ru/search/?query={query}")
            self.speak(f"Вот что мне удалось найти на RuTube по запросу \"{query}\"")
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Поиск на RuTube\"")
            traceback.print_exc()


    def search_website(self, query):
        query = query.replace("открой ", "").replace("open ", "")
        self.speak(f"Произвожу поиск сайта \"{query}\"")
        try:
            webbrowser.open(f"https://www.{query}")
            self.speak(f"Открываю \"{query}\"")
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Открыть website\"")
            traceback.print_exc()


    def translate(self, query):
        if "с английского" in query:
            lang_src = "en"
            lang_dest = "ru"
        elif "на английский" in query:
            lang_src = "ru"
            lang_dest = "en"
        else:
            self.speak("Извините, поддерживается только перевод с английского на русский и наоборот")
            return

        query = query.replace("переведи с английского ", "").replace("переведи на английский ", "")

        try:
            translator = GoogleTranslator(source=lang_src, target=lang_dest)
            translated_text = translator.translate(query)
            self.speak(translated_text)
        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Переводчик\"")
            traceback.print_exc()


    def get_weather(self, query):
        weather_api_key = "d96f9e7a991662805b2a55530dd73573"
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        try:
            owm = OWM(weather_api_key, config_dict)
            mgr = owm.weather_manager()

            if "в городе" in query:
                city = query.split(" ")[-1]
            else:
                city = self.city

            observation = mgr.weather_at_place(city)
            weather = observation.weather

            status = weather.detailed_status
            temp = weather.temperature('celsius')["temp"]
            wind = weather.wind()["speed"]
            pressure = int(weather.pressure["press"] / 1.333)

            self.speak(f"В городе {city} {status}")
            self.speak(f"Температура {temp} градусов по Цельсию")
            self.speak(f"Скорость ветра {wind} метров в секунду")
            self.speak(f"Давление {pressure} миллиметров ртутного столба")

        except Exception as e:
            self.speak("Произошла ошибка работы модуля \"Погода\"")
            traceback.print_exc()


    def time(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.speak(f"Текущее время: {current_time}")


    def start_app(self, query):
        query = query.replace("запусти ", "")
        try:
            if "edge" in query:
                subprocess.run("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
            elif "калькулятор" in query:
                subprocess.run(["calc"])
            elif "браузер" in query:
                subprocess.run(["start", "chrome"])
        except Exception as e:
            self.speak("Не удалось запустить приложение")
            traceback.print_exc()


    def play_music(self):
        music_dir = Path("C:\\MyMusic")
        try:
            music_files = list(music_dir.glob("*"))
            if music_files:
                chosen = random.choice(music_files)
                os.startfile(chosen)
            else:
                self.speak("В папке с музыкой нет файлов")
        except Exception as e:
            self.speak("Не удалось воспроизвести музыку")
            traceback.print_exc()

class BotTranslate:
    def __init__(self, language="ru"):
        self.language = language
        try:
            with open("translations.json", "r", encoding="UTF-8") as file:
                self.translations = json.load(file)
        except FileNotFoundError:
            print("Файл translations.json не найден. Создайте файл с переводами.")
            self.translations = {}

    def get(self, text: str):
        if text in self.translations:
            return self.translations[text].get(self.language, text)
        print(f"Для фразы: {text} нет перевода.")
        return text

# Класс графического интерфейса
class AssistantGUI:
    def __init__(self, master, assistant):
        self.master = master
        self.assistant = assistant
        master.title(f"Голосовой помощник {assistant.bot_name_ru}")
        master.geometry("800x600")
        master.configure(bg='#f0f0f0')

        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TFrame', background='#f0f0f0')

        self.top_frame = ttk.Frame(master)
        self.top_frame.pack(pady=10, fill=tk.X)

        try:
            self.logo_img = Image.open("logo.png").resize((80, 80), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = tk.Label(self.top_frame, image=self.logo_photo, bg='#f0f0f0')
            self.logo_label.pack(side=tk.LEFT, padx=10)
        except:
            self.logo_label = tk.Label(self.top_frame, text="🤖", font=('Arial', 24), bg='#f0f0f0')
            self.logo_label.pack(side=tk.LEFT, padx=10)

        self.title_label = tk.Label(
            self.top_frame,
            text=f"{assistant.bot_name_ru} - ваш голосовой помощник",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        self.title_label.pack(side=tk.LEFT, pady=10)

        self.chat_frame = ttk.Frame(master)
        self.chat_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=('Arial', 10),
            bg='white',
            fg='black'
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        self.control_frame = ttk.Frame(master)
        self.control_frame.pack(pady=10, fill=tk.X)

        self.listen_btn = ttk.Button(
            self.control_frame,
            text="Слушать",
            command=self.start_listening,
            style='TButton'
        )
        self.listen_btn.pack(side=tk.LEFT, padx=5, ipadx=20)

        self.stop_btn = ttk.Button(
            self.control_frame,
            text="Стоп",
            command=self.stop_assistant,
            style='TButton'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, ipadx=20)

        self.exit_btn = ttk.Button(
            self.control_frame,
            text="Выход",
            command=master.quit,
            style='TButton'
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=5, ipadx=20)

        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = tk.Label(
            master,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Arial', 9),
            bg='#e0e0e0'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.add_message(f"{self.assistant.bot_name_ru}",
                         "Добрый день! Я ваш голосовой помощник. Нажмите кнопку 'Слушать' или скажите команду.")

    def add_message(self, sender, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def update_status(self, message):
        self.status_var.set(message)

    def start_listening(self):
        self.update_status("Слушаю...")
        self.add_message("Вы", "[нажмите кнопку и говорите]")
        self.listen_btn.config(state=tk.DISABLED)

        threading.Thread(target=self.process_command, daemon=True).start()

    def process_command(self):
        query = self.assistant.record()
        if query:
            self.add_message("Вы", query)
            self.process_query(query)
        else:
            self.add_message(f"{self.assistant.bot_name_ru}", "Я не расслышал ваш запрос. Пожалуйста, повторите.")

        self.master.after(0, self.reset_listen_button)

    def reset_listen_button(self):
        self.listen_btn.config(state=tk.NORMAL)
        self.update_status("Готов к работе")

    def process_query(self, query):
        query = query.lower()

        if ("википедия" in query) or ("википедии" in query) or ("wikipedia" in query):
            self.assistant.search_wiki(query)
        elif ("гугл" in query) or ("google" in query):
            self.assistant.search_google(query)
        elif ("яндекс" in query) or ("yandex" in query):
            self.assistant.search_yandex(query)
        elif ("ютуб" in query) or ("youtube" in query):
            self.assistant.search_youtube(query)
        elif ("рутуб" in query) or ("rutube" in query):
            self.assistant.search_rutube(query)
        elif ("открой" in query) or ("open" in query):
            self.assistant.search_website(query)
        elif ("переведи" in query) or ("перевод" in query) or ("translate" in query):
            self.assistant.translate(query)
        elif ("время" in query) or ("time" in query):
            self.assistant.time()
        elif ("запуск" in query) or ("запусти" in query) or ("start" in query):
            self.assistant.start_app(query)
        elif ("музыка" in query) or ("музыку" in query) or ("music" in query):
            self.assistant.play_music()
        else:
            self.add_message(f"{self.assistant.bot_name_ru}", "Я не понял ваш запрос. Пожалуйста, попробуйте еще раз.")

    def stop_assistant(self):
        self.update_status("Остановлен")
        self.add_message(f"{self.assistant.bot_name_ru}", "Работа приостановлена. Нажмите 'Слушать' для продолжения.")


if __name__ == "__main__":
    assistant = Bot()
    translator = BotTranslate(language=assistant.language)  # Используем правильное имя класса

    root = tk.Tk()
    gui = AssistantGUI(root, assistant)
    root.mainloop()
