import pyautogui
import time

print("Gerakkan mouse ke pojok KIRI-ATAS area game hitam...")
time.sleep(3) # Kamu punya 3 detik buat arahin mouse
x1, y1 = pyautogui.position()
print(f"Kiri-Atas dapet! -> X: {x1}, Y: {y1}")

print("\nSekarang gerakkan mouse ke pojok KANAN-BAWAH area game hitam...")
time.sleep(3)
x2, y2 = pyautogui.position()
print(f"Kanan-Bawah dapet! -> X: {x2}, Y: {y2}")

width = x2 - x1
height = y2 - y1

print("-" * 30)
print("COPY DATA INI KE SCRIPT BOT KAMU:")
print(f"monitor = {{'top': {y1}, 'left': {x1}, 'width': {width}, 'height': {height}}}")
print("-" * 30)