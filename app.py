from flask import Flask,  render_template, request, jsonify
from patent_search import patent_filter


app = Flask(__name__)

# a_query = 'Device and method for extending the lifespan of a shaft seal for an open-drive compressor. A device and method for extending the lifespan of a shaft seal for an open-drive compressor is provided. The device and method can also reduce and/or prevent deterioration of the shaft seal regardless of the operation condition of the open-drive compressor. The device and method can further reduce and/or prevent leakage of a lubricant and/or refrigerant that can cause deterioration of components within a transport refrigeration unit (TRU)'

@app.route('/')
def main():
    return render_template('index.html')

# @app.route('/print', methods=['GET','POST'])
# def print():
#     patent_filter(a_query=a_query)
#     return a_query

@app.route('/query', methods=['GET','POST'])
def get_query():
    query = request.form['query']
    b = patent_filter(a_query = query)
    return jsonify(result=b)
if __name__ == '__main__':
    app.run()



