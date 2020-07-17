from flask import Flask
import json
from linky import Linky

app = Flask(__name__)
app.config['SECRET_KEY']="thelinkysecret"
app.config['linky'] = Linky()

@app.route('/', methods=['GET'])
def get_news():
	try:
		data = app.config['linky'].trends
		links = app.config['linky'].links
		images = app.config['linky'].images
		headlines = app.config['linky'].headlines
		timings = app.config['linky'].timings
		json_data = json.dumps({'data':data, 'links':links, 'images':images, 'headlines':headlines, 'timings':str(timings)})
		return json_data
	except:
		json_data = json.dumps({'data':"data", 'links':"links", 'images':"images", 'headlines':"headlines", 'timings':'timings'})
		return json_data



if __name__ == "__main__":
	app.run(host='127.0.0.1', port=8000)
	