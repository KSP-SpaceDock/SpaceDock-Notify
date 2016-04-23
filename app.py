from flask import Flask, request
import configparser
import json
import os
import requests
import threading
import queue
from subprocess import call
app = Flask(__name__)

#Config
config = configparser.ConfigParser()
def loadconfig():
    if not os.path.isfile('config.ini'):
        config['notify'] = { 'address': '127.0.0.1', 'port': '8085', 'api-url': 'http://spacedock.info/api/mod/', 'notify-urls': json.dumps(['http://ckan-url/']), 'netkan-path': 'NetKAN'}
        with open('config.ini', 'w') as f:
            config.write(f)
    config.read('config.ini')
loadconfig()
#Threading
worker_data = queue.Queue()

def process_mod(mod_id, event_type):
    print("Processing mod " + str(mod_id))
    wd = config['notify']['netkan-path']
    call(['git', 'fetch', 'origin'], cwd=wd)
    call(['git', 'reset', '--hard', 'origin/master'], cwd=wd)
    identifiers = list()
    netkan_path = os.path.join(wd, "NetKAN")
    kref_match = '#/ckan/spacedock/' + str(mod_id)
    for filename in os.listdir(netkan_path):
        file_path = os.path.join(netkan_path, filename)
        if not filename.endswith('.netkan'):
            continue
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, 'r') as f:
                mod_data = json.load(f)
                if not '$kref' in mod_data:
                    continue
                mod_identifier = mod_data['identifier']
                mod_kref = mod_data['$kref']
                if mod_kref != kref_match:
                    continue
                print(mod_identifier + ": " + mod_kref)
                identifiers.append(mod_identifier)
        except Exception as detail:
            print("Error: ", detail)
    if len(identifiers) > 0:
        r = requests.get(config['notify']['api-url'] + str(mod_id))
        if r.status_code != 200:
            return
        api_data = r.json()
        send_data = { 'id': mod_id, 'event_type': event_type, 'identifiers': identifiers, 'api_data': api_data }
        send_data_text = json.dumps(send_data)
        for notify_url in json.loads(config['notify']['notify-urls']):
            print('Sending to ' + notify_url)
            try:
                requests.post(notify_url, data=send_data_text)
            except Exception as detail:
                print("Error: ", detail)
        print("Processing mod " + str(mod_id) + " complete")
    

def worker_loop():
    while True:
        try:
            work = worker_data.get()
            mod_id = work['mod_id']
            event_type = work['event_type']
            process_mod(mod_id, event_type)
        except Exception as detail:
            print("Error: ", detail)
 
worker_thread = threading.Thread(target=worker_loop)
worker_thread.daemon = True
worker_thread.start()

@app.route('/')
def ignore_request():
    return 'Ignoring request'

@app.route('/notify/', methods=['POST'])
def notify():
    try:
        mod_id_string = request.form['mod_id']
        event_type = request.form['event_type']
        mod_id = int(mod_id_string)
        put_data = { 'mod_id': mod_id, 'event_type': event_type }
        worker_data.put(put_data)
        return 'Notifying for mod ' + mod_id_string
    except Exception as detail:
        return 'Error processing request: ' + detail

#Webhook
if __name__ == '__main__':
    app.run(config['notify']['address'], int(config['notify']['port']), debug=True)

