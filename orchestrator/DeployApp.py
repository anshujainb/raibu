from flask import Flask,request
from flask import json
from flask import Response
from flask import make_response
from bson.json_util import dumps
import pymongo


app = Flask(__name__)

@app.route('/deploy',methods=['post'])
def deploy():
    data=json.dumps(request.json)
    obj=json.loads(data)
    return getDataFromdb(obj)
    

def getDataFromdb(obj):
    id='rb-'+obj['clientName']
    print("*******"+id)

    connection = pymongo.MongoClient("mongodb://localhost", 27017)

    db = connection.raibu
    raibuClients=db.raibuClients

    res=[]
    for doc in raibuClients.find({'clientId':id}):
        res.append(doc)

    #rp = dumps(res)
    
    listOfIp=[]
    for data in (res[0]['VmList']):
        listOfIp.append(data['publicIp'])
    rp=dumps(listOfIp)

    print(listOfIp)

   

    #rp = json.dumps(res,default=json_util.default)
    #rp = json.dumps(res)

    #rp = str(res)
    
    #print(rp)

    return rp
   



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
    #app.run(host='0.0.0.0',port=8001)