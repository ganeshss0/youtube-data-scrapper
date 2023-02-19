import googleapiclient.discovery
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import json
from handle_mongo import Store_Mongo
import logging


app = Flask(__name__)
CORS(app)
logging.basicConfig(filename = 'app.log', filemode='a', level = logging.DEBUG, format = '%(asctime)s %(levelname)s: %(message)s')

class youtube:
    SERVICE = "youtube"
    VERSION = "v3"
    API_KEY = "AIzaSyCY6KIKX8HV0-RyfjMwhMihpwSMZ4Im4Jk"



    def get_response(self):
        logging.info('Connected Youtube Server')
        return googleapiclient.discovery.build(self.SERVICE, self.VERSION, developerKey = self.API_KEY)

    def search(self, client, query, query_type):
        response =  client.search().list(
            q=query, 
            part = 'id,snippet',
            type = query_type,
            maxResults = 25)
        logging.info('Fetch Results Success')
        return response.execute()

    def channel(self, client, id):
        channel = client.channels().list(id = id, part = 'statistics')
        logging.info('Fetch Channel Success')
        return channel.execute()

    def video(self, client, id):
        video = client.videos().list(id = id,  part = 'statistics')
        logging.info('Fetch Video Success')
        return video.execute()
    

    
        
@app.route('/', methods = ['GET', 'POST'])
@cross_origin()
def homepage():
    logging.info('Homepage Rendered')
    return render_template('index.html')

@app.route('/search', methods = ['POST'])
@cross_origin()
def search_results():
    query = request.form['query']
    query_type = request.form['type']
    find = youtube()
    response = find.get_response()
    results = find.search(response, query, query_type)
    return render_template(f'{query_type}.html', results = results)



@app.route('/result', methods = ['POST'])
@cross_origin()
def get_results():
    keys = request.form['id-type'].split(',')
    ID = keys[0]
    query_type = keys[1].split('#')[-1]
    find = youtube()
    response = find.get_response()

    if query_type == 'channel':
        results = find.channel(response, ID)
        template = 'result_channel.html'
    elif query_type == 'video':
        results = find.video(response, ID)
        template = 'result_video.html'
    with open('Result.json', 'w') as file:
        json.dump(results, file)
        logging.info('Result.json Created')
    return render_template('result_video.html', results = results)

@app.route('/mongo', methods = ['GET','POST'])
@cross_origin()
def mongo():
    return render_template('mongo.html')

@app.route('/save', methods = ['POST'])
@cross_origin()
def save_to_mongo():
    connection_string = request.form['connection_string']
    store = Store_Mongo(connection_string)
    if store.test():
        with open('Result.json') as file:
            data = json.load(file)
        store.upload(data)
        return '<h1>Successful</h1>'
    else:
        return '<h1>Invalid Credentials</h1>'





































if __name__ == '__main__':
    logging.info('App Started')
    app.run(host = '0.0.0.0')