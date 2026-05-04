import network
import socket
import machine


# --- AYARLAR ---
SSID = 'abdo'
PASSWORD = 'abdulrahman1622'
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
                html_icerik = ''' <!DOCTYPE html>
                            <html lang="tr">

                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>LED Kontrolü</title>
                                <style>
                                    body {
                                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                        display: flex;
                                        flex-direction: column;
                                        align-items: center;
                                        justify-content: center;
                                        height: 100vh;
                                        margin: 0;
                                        background-color: #f0f2f5;
                                        color: #333;
                                    }

                                    .container {
                                        background: white;
                                        padding: 3rem 5rem;
                                        border-radius: 12px;
                                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                                        text-align: center;
                                    }

                                    h1 {
                                        margin-top: 0;
                                        margin-bottom: 2rem;
                                        color: #1a1a1a;
                                    }

                                    .led-indicator {
                                        width: 120px;
                                        height: 120px;
                                        border-radius: 50%;
                                        background-color: #333;
                                        margin: 0 auto 2.5rem;
                                        transition: all 0.3s ease;
                                        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.8);
                                    }

                                    .led-indicator.on {
                                        background-color: #e50606;
                                        /* Sarı ışık */
                                        box-shadow: 0 0 40px #ff3b3b, inset 0 0 20px rgba(255, 255, 255, 0.8);
                                    }

                                    .button-group {
                                        display: flex;
                                        gap: 1.5rem;
                                        justify-content: center;
                                    }

                                    button {
                                        padding: 12px 30px;
                                        font-size: 1.2rem;
                                        border: none;
                                        border-radius: 8px;
                                        cursor: pointer;
                                        transition: transform 0.1s, opacity 0.2s, box-shadow 0.2s;
                                        font-weight: 600;
                                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                    }

                                    button:active {
                                        transform: scale(0.95);
                                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                    }

                                    .btn-on {
                                        background-color: #4CAF50;
                                        color: white;
                                    }

                                    .btn-on:hover {
                                        opacity: 0.9;
                                    }

                                    .btn-off {
                                        background-color: #f44336;
                                        color: white;
                                    }

                                    .btn-off:hover {
                                        opacity: 0.9;
                                    }

                                    .status-text {
                                        margin-top: 2rem;
                                        font-weight: bold;
                                        font-size: 1.3rem;
                                        color: #555;
                                        transition: color 0.3s ease;
                                    }
                                </style>
                            </head>

                            <body>

                                <div class="container">
                                    <h1>Işık Kontrolü</h1>

                                    <!-- Işık görseli -->
                                    <div class="led-indicator" id="led"></div>

                                    <!-- Butonlar -->
                                    <div class="button-group">
                                        <button class="btn-on" onclick="toggleLED(true)">YAK</button>
                                        <button class="btn-off" onclick="toggleLED(false)">SÖNDÜR</button>
                                    </div>

                                    <!-- Yazılı durum -->
                                    <div class="status-text" id="status">Durum: Kapalı</div>
                                </div>

                                <script>
                                    function toggleLED(turnOn) {
                                        const led = document.getElementById('led');
                                        const statusText = document.getElementById('status');

                                        if (turnOn) {
                                            led.classList.add('on');
                                            statusText.innerText = 'Durum: Açık';
                                            statusText.style.color = '#fbc02d'; // Sarımsı renk

                                            // MicroPython sunucusuna LED açma isteği gönder (GET /led/on)
                                            fetch('/led/on').catch(err => console.error(err));
                                        } else {
                                            led.classList.remove('on');
                                            statusText.innerText = 'Durum: Kapalı';
                                            statusText.style.color = '#f44336'; // Kırmızı renk

                                            // MicroPython sunucusuna LED kapama isteği gönder (GET /led/off)
                                            fetch('/led/off').catch(err => console.error(err));
                                        }
                                    }
                                </script>
                            </body>

                            </html>
                             '''
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nConnection: close\r\n\r\n' + html_icerik
            
            cl.send(response.encode('utf-8'))
        except Exception as e:
            print('Hata oluştu:', e)
        finally:
            cl.close()

# Uygulamayı Çalıştır
connect_wifi()
start_server()
