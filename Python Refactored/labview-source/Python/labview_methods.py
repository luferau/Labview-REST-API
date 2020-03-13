import json

import requests


def getDocRev(inputNames, docId, apiToken, env):
    inputNames = json.loads(inputNames)
    URL = ("https://api.%senlil.io/api/v1/document_revisions/external/%s/draft" %(env, docId))
    r = requests.get(url = URL, headers={"accept":"application/json", "Authorization": apiToken})
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        return [err.response.text]
    data = r.json()
    revId = data["id"]
    for k, v in inputNames.items():
        for s in data['formDocument']['formTemplate']['schema']:
            if s['label'] == v:
                inputNames[k] = s['name']
    inputValues = inputNames.copy()
    for k,v in inputValues.items():
        for s,val in data['formInput'].items():
            if s == v:
                inputValues[k] = val
    validRes = { "statusCode": r.status_code }
    array = [json.dumps(validRes), json.dumps(inputNames), json.dumps(inputValues), revId, env]
    return array

def patchDocRev(inputNames, inputValues, vout, docRevId):
    body = {
        "formInput": {}
    }
    inputNames = json.loads(inputNames)
    inputValues = json.loads(inputValues)
    inputValues["Vout"] = str(vout)
    for k, v in inputNames.items():
        body["formInput"][v] = k
    for k, v in body["formInput"].items():
        for s, val in inputValues.items():
            if v == s:
                body["formInput"][k] = val

    URL = ("https://api.dev.enlil.io/api/v1/document_revisions/external/%s" % docRevId)
    response = requests.put(url = URL, data=json.dumps(body), headers={"accept":"application/json", "Content-Type": "application/json", "Authorization":"apitoken 475eef11-95b9-4f32-9221-3162004815ef:f20a91a0-c04e-4d32-b0b4-337e6e91bde7"})
    data = response.json()

    return [json.dumps(data['formInput'])]

def uploadFileUpdateDocRev(documentRevisionId, paths, apiToken, XYSeries, XYParallel, inputNames, inputValues, env):
    UPLOAD_URL = "https://api.%senlil.io/api/v1/attachments/external/upload" % env
    PUT_URL = "https://api.%senlil.io/api/v1/document_revisions/external/%s" %(env, documentRevisionId) 
    ids = []
    for x in paths:
        files = { "file": open('%s' % x, 'rb')}
        res = requests.post(url = UPLOAD_URL, headers = {"accept": "application/json", "Authorization": apiToken}, files=files)
        try:
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            return [err.response.text]
        data = res.json()
        print(data['id'])
        ids.append({ "id": data['id'] })

    inputNames = json.loads(inputNames)
    inputValues = json.loads(inputValues)
    inputValues["Series"] = XYSeries
    inputValues["Parallel"] = XYParallel
    body = {
        "attachments": ids,
        "formInput": {}
    }
    for k, v in inputNames.items():
        body["formInput"][v] = k
    for k, v in body["formInput"].items():
        for s, val in inputValues.items():
            if v == s:
                body["formInput"][k] = val
    res = requests.put(url = PUT_URL, data=json.dumps(body), headers = {"accpet": "application/json", "Content-Type": "application/json", "Authorization": apiToken})
    try:
        res.raise_for_status()
    except requests.exceptions.RequestException as err:
        return [err.response.text]
    data = res.json()
    data_patch = res.json()
    validRes = { "statusCode": res.status_code }
    return [json.dumps(validRes), json.dumps(data_patch["attachments"]), json.dumps(data_patch["formInput"])]

