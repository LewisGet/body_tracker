import cv2
import time
import datetime
import requests
from bs4 import BeautifulSoup


# 設置 API 網址
api_url = "http://127.0.0.1:8000/record/image_log/create"

# 獲取 CSRF token
def get_csrf_token():
    response = requests.get(api_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    return csrf_token


def create_image_post(frame, timestamp):
    _, img_encoded = cv2.imencode('.jpg', frame)

    try:
        csrf = get_csrf_token()
    except:
        return False

    files = {'image': ('image.jpg', img_encoded.tobytes(), 'image/jpeg')}
    data = {'timestamp': timestamp, 'csrfmiddlewaretoken': csrf}
    headers = {'X-CSRFToken': csrf}

    response = requests.post(api_url, files=files, data=data)

    return response


# init cam
cap = cv2.VideoCapture(0)

# test available cam
if not cap.isOpened():
    print("cam init fail")
    exit()


while True:
    ret, frame = cap.read()

    if not ret:
        print("cam no signal")
        break

    timestamp = datetime.datetime.fromtimestamp(float(time.time()))

    create_image_post(frame, timestamp)
    time.sleep(1000 / 40 / 1000)
