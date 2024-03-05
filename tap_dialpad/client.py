import requests
import time


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Authorization':f'Bearer {self.api_key}'}
        self.session = requests.Session()
        self.session.headers = self.headers
        self.stats_url = 'https://dialpad.com/api/v2/stats'

    def initiate_stats_request(self, days_ago_end=1):
        body = {'days_ago_end': days_ago_end,
                'days_ago_start': 1,
                'export_type': 'records',
                'stat_type': 'recordings',
                'timezone': 'UTC'}

        resp = self.session.post(self.stats_url, data=body)
        return resp.json()['request_id']

    def poll_stats(self, request_id):
        body = {'id': request_id}
        while(1):
            resp = self.session.get(self.stats_url, params=body)
            json = resp.json()
            if (json['status'] == 'processing'):
                time.sleep(1)
            else:
                return json

    def download_recording(self, recording_url):
        return self.session.get(recording_url)

def get_recordings(config, days_ago_end):
    client = Client(config['api_key'])
    stats_id = client.initiate_stats_request(days_ago_end)
    stats_res = client.poll_stats(stats_id)

    if (stats_res['status'] == 'failed'):
        raise Exception("[Client] Unknown failure on stats request. Failed to retrieve recordings.")

    url = stats_res['download_url']
    csv_data = requests.get(url, params={'apikey': client.api_key}).text
    from io import StringIO
    import csv
    rows = csv.DictReader(StringIO(csv_data, newline=''))
    return list(rows)
