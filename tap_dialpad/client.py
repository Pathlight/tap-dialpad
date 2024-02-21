import requests
import time


class Client:
    def __init__(self):
        self.api_key = "secret"
        self.headers = {'Authorization':f'Bearer {self.api_key}'}
        self.session = requests.Session()
        self.session.headers = self.headers
        self.stats_url = 'https://dialpad.com/api/v2/stats'

    def initiate_stats_request(self):
        body = {'days_ago_end': 2,
                'days_ago_start': 1,
                'export_type': 'records',
                'stat_type': 'recordings',
                'timezone': 'UTC'}

        resp = self.session.post(self.stats_url, data=body)
        print(f"[Client] Inititiate stats response:{resp.json()}")
        return resp.json()['request_id']

    def poll_stats(self, request_id):
        body = {'id': request_id}
        while(1):
            resp = self.session.get(self.stats_url, params=body)
            print(f'Poll stats:{resp.text}')
            json = resp.json()
            if (json['status'] == 'processing'):
                print(f"[Client] request id:{request_id} still processing")
                time.sleep(1)
            else:
                return json


    def download_recording(self, recording_url):
        return self.session.get(recording_url)

def get_tap_data():
    client = Client()
    stats_id = client.initiate_stats_request()
    stats_res = client.poll_stats(stats_id)

    if (stats_res['status'] == 'failed'):
        print('[Client] Failed to poll stats request.')
        return 1

    url = stats_res['download_url']
    print(f"[Client] Attempting to download:{url}")
    csv_data = requests.get(url, params={'apikey': client.api_key}).text
    from io import StringIO
    import csv
    rows = csv.DictReader(StringIO(csv_data, newline=''))
    print("[Client] Retrieved rows")

    for row in rows:
        recording_url = row['recording_url']
        print(f'[Client] downloading record:{recording_url}')
        recording = requests.get(recording_url, headers=client.headers)
        print(f'[Client] download result:{recording.status_code}')
        with open("recording.mp3", 'wb') as f:
            f.write(recording.content)
        return 0

if __name__ == '__main__':
    print("running program")
    get_tap_data()



