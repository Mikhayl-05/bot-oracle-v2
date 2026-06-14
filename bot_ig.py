import cv2
import numpy as np
import mss
import keyboard
import win32api
import threading
import time

# ==========================================================
# 1. KONFIGURASI SESUAI KOORDINAT BARU
# ==========================================================
MONITOR = {'top': 93, 'left': 169, 'width': 501, 'height': 896}

# Area scan dari 25% sampai 90% tinggi layar
SCAN_AREA = {
    'top': MONITOR['top'] + int(MONITOR['height'] * 0.25),
    'left': MONITOR['left'],
    'width': MONITOR['width'],
    'height': int(MONITOR['height'] * 0.65)
}

PADDLE_Y_GLOBAL = MONITOR['top'] + int(MONITOR['height'] * 0.94)
PADDLE_Y_LOCAL = SCAN_AREA['height'] 
LIMIT_KANAN = MONITOR['width']

class BotOracleV2:
    def __init__(self):
        self.latest_frame = None
        self.display_frame = None # Untuk jendela debug
        self.running = True
        self.history = []
        self.predicted_x = MONITOR['width'] // 2
        
    def predict_intercept(self, x, y, dx, dy):
        """Menghitung titik jatuh bola dengan pantulan dinding zigzag"""
        if dy <= 0: return None
        
        dist_y = PADDLE_Y_LOCAL - y
        steps = dist_y / dy
        target_x = x + (dx * steps)
        
        # Logika Pantulan Berulang
        while target_x < 0 or target_x > LIMIT_KANAN:
            if target_x > LIMIT_KANAN:
                target_x = 2 * LIMIT_KANAN - target_x
            elif target_x < 0:
                target_x = -target_x
                
        return target_x

    def capture_loop(self):
        with mss.mss() as sct:
            while self.running:
                sct_img = sct.grab(SCAN_AREA)
                raw_frame = np.array(sct_img)
                # Simpan versi kecil untuk proses, versi normal untuk display
                self.latest_frame = raw_frame[::2, ::2]
                self.display_frame = raw_frame.copy()

    def run(self):
        print(f"=== BOT ORACLE V2 DEBUG MODE ===")
        t = threading.Thread(target=self.capture_loop, daemon=True)
        t.start()
        
        last_x = MONITOR['width'] // 2
        
        try:
            while True:
                if keyboard.is_pressed('q'):
                    self.running = False
                    break
                
                if self.latest_frame is None or self.display_frame is None: 
                    continue

                # --- PROSES IMAGE ---
                gray = cv2.cvtColor(self.latest_frame, cv2.COLOR_BGRA2GRAY)
                _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                best_ball = None
                max_y = -1
                
                for cnt in contours:
                    if 25 < cv2.contourArea(cnt) < 1000:
                        x_box, y_box, w_box, h_box = cv2.boundingRect(cnt)
                        if y_box > max_y:
                            max_y = y_box
                            best_ball = ( (x_box + w_box // 2) * 2, (y_box + h_box // 2) * 2 )

                # --- LOGIKA PREDIKSI ---
                if best_ball:
                    self.history.append(best_ball)
                    if len(self.history) > 2: self.history.pop(0)
                    
                    if len(self.history) == 2:
                        p1, p2 = self.history[0], self.history[1]
                        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                        
                        res_x = self.predict_intercept(p2[0], p2[1], dx, dy)
                        if res_x is not None:
                            self.predicted_x = res_x
                            final_x_global = MONITOR['left'] + self.predicted_x
                            
                            if abs(final_x_global - last_x) > 2:
                                win32api.SetCursorPos((int(final_x_global), PADDLE_Y_GLOBAL))
                                last_x = final_x_global

                    # --- VISUAL DEBUGGER (Opsional, makan sedikit CPU) ---
                    # Gambar titik bola dan garis prediksi ke dasar
                    cv2.circle(self.display_frame, best_ball, 10, (0, 255, 0), 2)
                    cv2.line(self.display_frame, best_ball, (int(self.predicted_x), PADDLE_Y_LOCAL), (0, 0, 255), 2)

                # Tampilkan jendela visi bot
                cv2.imshow("Visi Bot (Garis Merah = Prediksi)", self.display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                                
        finally:
            self.running = False
            cv2.destroyAllWindows()
            print("Bot Berhenti.")

if __name__ == "__main__":
    bot = BotOracleV2()
    bot.run()