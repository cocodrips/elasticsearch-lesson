import datetime
import json
import urllib2

index_ = "service_name"
type_ = "daily_data"
id_format_ = "{date}_{age}_{last_login}"
url_ = "http://localhost:9200/{index}/{type}/{id}"

with open('data/elastic_sample.json', 'r') as f:
    data = json.load(f)

    for d in data['data']:
        status = d['status']
        date = str(d['status']['date'])
        d['@timestamp'] = date[:4] + "-" + date[4:6] + "-" + date[6:]

        id_ = id_format_.format(date=status['date'],
                                age=status['age'],
                                last_login=status['last_login'])

        
        post_data = json.dumps(d)
        url = url_.format(index=index_,
                          type=type_,
                          id=id_)
        print id_, url, post_data

        req = urllib2.Request(url,
                              post_data,
                              {'Content-Type': 'application/json'})

        f = urllib2.urlopen(req)
        response = f.read()
        print response
        f.close()