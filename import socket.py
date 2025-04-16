import socket
import datetime
import ssl
import os

HOST = '0.0.0.0'
PORT = 443

student = "Puzikov Andrey Vyacheclavovich"
message = "First https server"

# Проверка существования сертификата и ключа
certfile = 'certificate.crt'  # Лучше использовать относительные пути
keyfile = 'privateKey.key'

if not os.path.exists(certfile) or not os.path.exists(keyfile):
    print(f"Ошибка: Не найдены файлы сертификата ({certfile}) или ключа ({keyfile})")
    exit(1)

def create_response():
    headers = {
        'Server': 'MyServer',
        'Date': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'Content-Type': 'text/html; charset=utf-8',
        'Connection': 'close',
        'Access-Control-Allow-Origin': '*',  # Разрешить запросы с любого origin
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',  # Разрешенные методы
        'Access-Control-Allow-Headers': 'Content-Type',  # Разрешенные заголовки
    }

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<title>Python HTTPS Server</title>
</head>
<body>
<h1>Request time: {datetime.datetime.now().strftime("%H:%M:%S")}</h1>
<h2>Server made by: {student}</h2>
<p>{message}</p>
</body>
</html>"""

    response = "HTTP/1.1 200 OK\r\n"
    response += "\r\n".join(f"{key}: {value}" for key, value in headers.items())
    response += "\r\n\r\n" + html_content
    return response

def handle_request(conn):
    try:
        request = conn.recv(1024).decode('utf-8', errors='ignore')
        print(f"Получен запрос:\n{request[:500]}...")  # Логируем начало запроса
        
        response = create_response()
        conn.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
    finally:
        conn.close()

def log_connection(address):
    try:
        with open("connections.log", "a", encoding='utf-8') as log_file:
            log_file.write(f"[{datetime.datetime.now()}] Connection from {address[0]}:{address[1]}\n")
    except Exception as e:
        print(f"Ошибка записи в лог: {e}")

# Создание SSL контекста
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=certfile, keyfile=keyfile)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"Сервер запущен на https://{HOST}:{PORT}")

    try:
        while True:
            conn, addr = sock.accept()
            log_connection(addr)
            print(f"Подключение от {addr[0]}:{addr[1]}")
            
            try:
                with context.wrap_socket(conn, server_side=True) as secure_conn:
                    handle_request(secure_conn)
            except ssl.SSLError as e:
                print(f"SSL ошибка: {e}")
            finally:
                conn.close()
    except KeyboardInterrupt:
        print("\nСервер остановлен")