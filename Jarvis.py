# [All existing imports remain unchanged]
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import pyjokes
import os
import psutil
import pyautogui
import ctypes
import socket
import time
import threading
import json
import subprocess
from PIL import Image, ImageDraw
import pystray
import sys
import requests
from datetime import datetime

# Global app and process mappings
app_paths = {
    "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vscode": r"C:\\Users\\Manjunath\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "whatsapp": "uwp",
    "zoom": "uwp_zoom",
    "outlook": "outlook.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "word": "winword.exe",
    "teamviewer": "TeamViewer.exe",
    "telegram": r"C:\\Users\\Manjunath\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe",
}

process_map = {
    "chrome": "chrome.exe",
    "vscode": "Code.exe",
    "notepad": "notepad.exe",
    "calculator": "Calculator.exe",
    "paint": "mspaint.exe",
    "outlook": "OUTLOOK.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "word": "WINWORD.EXE",
    "teamviewer": "TeamViewer.exe",
    "telegram": "Telegram.exe",
    "zoom": "Zoom.exe"
}

# Debug control
DEBUG = False  # Set to True to enable debug logs

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

MEMORY_FILE = "jarvis_memory.json"

# Initialize voice engine only once
engine = pyttsx3.init()
engine.setProperty('rate', 187)  # Set speech speed
engine.setProperty('volume', 1.0)

# Try to set male Indian voice (Ravi)
for voice in engine.getProperty('voices'):
    if "ravi" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break


def speak(text, emotion=None):
    print(f"Jarvis: {text}")
    try:
        # 🔊 Speak first
        engine.say(text)
        engine.runAndWait()

        # ✅ Then send to frontend (so text and voice feel in sync)
        try:
            requests.post("http://localhost:5000/api/jarvis_output", json={"response": text})
        except Exception as e:
            print(f"[HUD] Failed to send to frontend: {e}")

    except Exception as e:
        print(f"[ERROR] speak() failed: {e}")



user_name = "Manjunath"
honorific = "sir"
friends = sorted(["Vidya", "Ankush", "Rakshitha", "Manoj"], key=lambda x: x.lower())

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_memory():
    with open(MEMORY_FILE, "w") as file:
        json.dump(jarvis_memory, file)

jarvis_memory = load_memory()
jarvis_memory.setdefault("usage_stats", {})

def update_usage_stat(command_key):
    now = datetime.now()
    hour_block = f"{now.hour // 4 * 4:02d}-{(now.hour // 4 + 1) * 4 - 1:02d}"
    usage = jarvis_memory["usage_stats"].setdefault(command_key, {})
    usage[hour_block] = usage.get(hour_block, 0) + 1
    save_memory()

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except:
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False

def get_weather():
    try:
        response = requests.get("https://wttr.in/?format=%C+%t", timeout=5)
        if response.status_code == 200:
            raw = response.text.strip()
            if '+' in raw or '-' in raw:
                parts = raw.split()
                condition = ' '.join(parts[:-1])
                temperature = parts[-1].replace("+", "").replace("\u00b0C", "")
                return f"Currently, it's {condition.lower()} with a temperature of {temperature} degrees Celsius."
            else:
                return f"The weather is currently {raw.lower()}."
        else:
            return "Weather data is not available right now."
    except:
        return "Unable to fetch weather at the moment."

def background_report():
    battery = psutil.sensors_battery()
    percent = battery.percent if battery else "unknown"
    plugged = "charging" if battery and battery.power_plugged else "not charging"
    speak(f"The battery is at {percent} percent and is {plugged}.", emotion="calm")
    connection = "connected" if is_connected() else "disconnected"
    speak(f"Your Wi-Fi is currently {connection}.", emotion="calm")

def suggest_frequent_app():
    now = datetime.now()
    current_block = f"{now.hour // 4 * 4:02d}-{(now.hour // 4 + 1) * 4 - 1:02d}"
    usage = jarvis_memory.get("usage_stats", {})
    most_used = None
    max_count = 0
    for app, times in usage.items():
        if times.get(current_block, 0) > max_count:
            most_used = app
            max_count = times[current_block]

    if most_used and max_count >= 2:
        speak(f"By the way {honorific}, you've been using {most_used} often at this time. Shall I open it?", emotion="gentle")

        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print("[MIC] Waiting for yes/no to reopen recent app...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                response = recognizer.recognize_google(audio).lower()
                print(f"[USER]: {response}")

                affirmatives = ["yes", "yeah", "sure", "okay", "open it", "do it", "go ahead"]
                negatives = ["no", "not now", "don't", "nope"]

                if any(word in response for word in affirmatives):
                    speak(f"Opening {most_used} again.", emotion="happy")
                    open_app(most_used)
                elif any(word in response for word in negatives):
                    speak("Okay, not opening it.", emotion="calm")
                else:
                    speak("Okay, not opening it.", emotion="calm")

        except sr.WaitTimeoutError:
            print("[MIC] No response within 5 seconds.")
        except sr.UnknownValueError:
            print("[MIC] Couldn't understand response.")
        except Exception as e:
            print(f"[ERROR]: {str(e)}")


def greeting():
    hour = datetime.now().hour
    if 0 <= hour < 12:
        speak(f"Good morning,{honorific}!", emotion="happy")
    elif 12 <= hour < 16:
        speak(f"Good afternoon,{honorific}!", emotion="happy")
    else:
        speak(f"Good evening,{honorific}!", emotion="happy")
        
    speak("Welcome back.", emotion="Energetic")
    weather_report = get_weather()
    speak(weather_report, emotion="calm")    
    
def take_command(timeout=5, phrase_time_limit=8):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[MIC] Adjusting for ambient noise...")
        recognizer.pause_threshold = 1
        recognizer.energy_threshold = 400
        recognizer.adjust_for_ambient_noise(source)
        print("[MIC] Listening for voice...")

        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("[MIC] Timeout: No speech detected.")
            return ""
        except Exception as e:
            print(f"[MIC] Error during listening: {e}")
            return ""

    try:
        command = recognizer.recognize_google(audio, language='en-in').lower()
        print(f"[USER]: {command}")
        return command
    except sr.UnknownValueError:
        print("[MIC] Didn't understand audio.")
        #speak("Sorry, I didn't catch that.", emotion="sad")
        return ""
    except sr.RequestError as e:
        print(f"[MIC] Google API error: {e}")
        speak("Speech service is unavailable.", emotion="sad")
        return ""
    except Exception as e:
        print(f"[MIC] Unexpected recognition error: {e}")
        speak("There was a problem processing your voice.", emotion="sad")
        return ""


def open_app(command):
    debug_print(f"open_app() received: {command}")

    # If the command has 'close' or 'exit', skip opening
    if "close" in command or "exit" in command:
        debug_print("open_app() skipped due to close/exit keyword.")
        return False

    for key in app_paths:
        if key in command:
            debug_print(f"Matched open command for: {key}")
            update_usage_stat(key)
            try:
                if app_paths[key] == "uwp" and key == "whatsapp":
                    debug_print("Launching WhatsApp UWP")
                    os.system("start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
                elif app_paths[key] == "uwp_zoom" and key == "zoom":
                    debug_print("Launching Zoom UWP")
                    os.system("start shell:AppsFolder\\ZoomVideoCommunications.ZoomVideoConference_z0p05pxq00ajm!App")
                else:
                    os.startfile(app_paths[key])
            except:
                speak(f"I couldn't open {key}, {honorific}.", emotion="sad")
            return True

    return False


def close_app(command):
    debug_print(f"close_app() received: {command}")

    for key in process_map:
        if f"close {key}" in command or f"exit {key}" in command:
            debug_print(f"Matched close command for: {key}")
            update_usage_stat(f"close {key}")
            def kill_proc():
                try:
                    subprocess.call(["taskkill", "/f", "/im", process_map[key]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except:
                    pass
            threading.Thread(target=kill_proc, daemon=True).start()
            return True

    if "whatsapp" in command and ("close" in command or "exit" in command):
        update_usage_stat("close whatsapp")
        debug_print("Closing WhatsApp UWP app...")
        def kill_whatsapp():
            try:
                output = subprocess.check_output('tasklist', shell=True).decode()
                if "ApplicationFrameHost.exe" in output:
                    subprocess.call(["taskkill", "/f", "/im", "ApplicationFrameHost.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                debug_print(f"Error closing WhatsApp: {e}")
        threading.Thread(target=kill_whatsapp, daemon=True).start()
        return True

    return False



def system_control(command):
    if "screenshot" in command:
        update_usage_stat("screenshot")
        file = os.path.expanduser("~\\Desktop\\screenshot.png")
        pyautogui.screenshot(file)
        speak("Screenshot taken and saved to desktop.", emotion="happy")
        return True
    elif "battery" in command:
        battery = psutil.sensors_battery()
        speak(f"Battery is at {battery.percent} percent, {honorific}.", emotion="calm")
        return True
    elif "lock" in command:
        update_usage_stat("lock")
        speak("Locking the computer.", emotion="gentle")
        ctypes.windll.user32.LockWorkStation()
        return True
    elif "shutdown" in command:
        update_usage_stat("shutdown")
        speak("Shutting down the system.", emotion="serious")
        os.system("shutdown /s /t 1")
        return True
    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Volume muted.", emotion="gentle")
        return True
    elif "increase volume" in command:
        pyautogui.press("volumeup")
        speak("Volume increased.", emotion="happy")
        return True
    return False

def interpret(command):
    global last_failed_topic  # allow modification inside function

    if not command:
        return

    if 'your name' in command:
        speak("My name is Jarvis, your personal assistant.", emotion="gentle")

    elif 'my name' in command:
        speak(f"Your name is {user_name}, {honorific}.", emotion="happy")

    elif 'my friends' in command:
        speak(f"Your friends are: {', '.join(friends)}.", emotion="happy")

    elif 'time' in command:
        speak(datetime.now().strftime("The time is %I:%M %p"), emotion="calm")

    elif 'date' in command:
        speak(datetime.now().strftime("Today is %A, %B %d, %Y"), emotion="calm")

    elif 'wikipedia' in command:
        topic = command.replace('wikipedia', '').strip()
        speak("Searching Wikipedia...", emotion="gentle")
        try:
            summary = wikipedia.summary(topic, sentences=2)
            speak(summary, emotion="calm")
            last_failed_topic = None
        except:
            speak("Sorry, I couldn’t find anything on Wikipedia.", emotion="sad")
            last_failed_topic = topic

    elif command.startswith("what is") or command.startswith("what's") or command.startswith("who is") or command.startswith("tell me about"):
        try:
            topic = command.replace("jarvis", "").replace("what is", "").replace("what's", "").replace("who is", "").replace("tell me about", "").strip()
            speak(f"Let me look up {topic} for you.", emotion="curious")
            summary = wikipedia.summary(topic, sentences=2)
            speak(summary, emotion="joy")
            last_failed_topic = None
        except wikipedia.exceptions.DisambiguationError:
            speak(f"There are multiple results for {topic}. Can you be more specific?", emotion="calm")
            last_failed_topic = None
        except wikipedia.exceptions.PageError:
            speak("Sorry, I couldn't find anything on that. Want me to search online?", emotion="gentle")
            last_failed_topic = topic
        except:
            speak("I had trouble understanding that. Want me to search it online?", emotion="gentle")
            last_failed_topic = topic

    elif any(phrase in command for phrase in ["yes", "do it", "search it", "search online", "go ahead"]) and last_failed_topic:
        url = f"https://www.google.com/search?q={last_failed_topic.replace(' ', '+')}"
        speak(f"Searching Google for {last_failed_topic}", emotion="curious")
        webbrowser.open(url)
        last_failed_topic = None


    elif 'google' in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google", emotion="happy")

    elif 'youtube' in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube", emotion="happy")

    elif 'joke' in command:
        speak(pyjokes.get_joke(), emotion="happy")

    elif command.startswith("remember"):
        key_value = command.replace("remember", "").strip()
        if " is " in key_value:
            key, value = key_value.split(" is ", 1)
            jarvis_memory[key.strip()] = value.strip()
            speak(f"Okay, I will remember that {key.strip()} is {value.strip()}.", emotion="gentle")
            save_memory()
        else:
            speak("Please tell me like this: remember my birthday is July 10th", emotion="sad")

    elif command.startswith("what is") or command.startswith("what's"):
        query = command.replace("what is", "").replace("what's", "").strip()
        answer = jarvis_memory.get(query)
        if answer:
            speak(f"Your {query} is {answer}.", emotion="happy")
        else:
            speak(f"I don’t remember anything about your {query}.", emotion="sad")

    elif 'exit' in command or 'stop' in command or 'goodbye' in command:
        speak(f"Goodbye,{honorific}! Have a nice day.", emotion="gentle")
        sys.exit()

    elif close_app(command):
        return

    elif open_app(command):
        return

    elif system_control(command):
        return

    else:
        speak("I'm still learning, please try a different command.", emotion="sad")



def jarvis_listener():
    while True:
        print("Waiting for command...")
        full_query = take_command(timeout=5, phrase_time_limit=8)

        if not full_query:
            continue

        if "jarvis" in full_query:
            cleaned_command = full_query.replace("jarvis", "").strip()
            if cleaned_command:
                print("[Wake+Command Mode] Detected full command with 'Jarvis'")
                interpret(cleaned_command)
            else:
                # Only wake word detected, use fallback two-step method
                speak("Yes sir.", emotion="gentle")
                time.sleep(0.5)
                print("Listening for your command...")
                user_command = take_command(timeout=5, phrase_time_limit=8)
                if user_command:
                    interpret(user_command)
                else:
                    speak("I'm still learning. Please try a different command.", "gentle")
        else:
            print("Wake word not detected. Looping again...")


def quit_app(icon, item):
    icon.stop()
    os._exit(0)

def create_image():
    image = Image.new('RGB', (64, 64), color=(73, 109, 137))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill='white')
    return image

def tray_thread():
    icon = pystray.Icon("Jarvis")
    icon.icon = create_image()
    icon.menu = pystray.Menu(pystray.MenuItem("Quit", quit_app))
    icon.run()

def run_jarvis():

    # Now start the main greeting and status report
    greeting()
    background_report()

    # Suggest app only after full startup
    suggest_frequent_app()

    print("Jarvis Listener Started (running in foreground for debugging)")
    jarvis_listener()

if __name__ == "__main__":
    run_jarvis()


