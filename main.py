import network
import socket
import machine
import time

# --- AYARLAR ---
SSID = 'WIFI_ADINIZ'
PASSWORD = 'WIFI_SIFRENIZ'
LED_PIN = 2 # ESP32 üzerindeki dahili mavi LED (Genellikle GPIO 2'dir)

# 4. & 5. Boolean Değişkeni ve LED Kontrolü
led = machine.Pin(LED_PIN, machine.Pin.OUT)
led_state = False
led.value(0) # Başlangıçta kapalı

# 1. ESP32'yi İnternete Bağla
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('WiFi ağına bağlanılıyor...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print('.', end='')
    print('\nBağlantı Başarılı!')
    print('IP Adresi:', wlan.ifconfig()[0])
    print('Tarayıcıya bu IP adresini girerek siteye ulaşabilirsiniz.')

# HTML kodunu dosyadan al
def get_html():
    try:
        # 2. HTML kodunu alacak şekilde hazırla (Aynı dizindeki index.html'i oku)
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "<h1>Hata: index.html bulunamadi. ESP32 dosya sistemine yuklediginize emin olun.</h1>"

# 3. Portta Yayınla (Socket)
def start_server():
    global led_state
    
    # 80 Numaralı Web Portunu Dinle
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print('Web sunucusu 80 portunda yayında dinleniyor...')
    
    while True:
        cl, addr = s.accept()
        print('İstemci bağlandı:', addr)
        try:
            request = cl.recv(1024).decode('utf-8')
            istek_satiri = request.split('\n')[0]
            print('Gelen İstek:', istek_satiri)
            
            # API İsteklerini Kontrol Et
            if istek_satiri.find('GET /led/on') == 0:
                print('Durum: LED Yakılıyor')
                led_state = True
                led.value(1) # LED'i yak
                response = 'HTTP/1.1 200 OK\r\n\r\nLED ACILDI'
                
            elif istek_satiri.find('GET /led/off') == 0:
                print('Durum: LED Söndürülüyor')
                led_state = False
                led.value(0) # LED'i söndür
                response = 'HTTP/1.1 200 OK\r\n\r\nLED KAPATILDI'
                
            else:
                # Normal ana URL (/) girilirse, HTML sitesini döndür
                html_icerik = get_html()
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nConnection: close\r\n\r\n' + html_icerik
            
            cl.send(response.encode('utf-8'))
        except Exception as e:
            print('Hata oluştu:', e)
        finally:
            cl.close()

# Uygulamayı Çalıştır
connect_wifi()
start_server()
