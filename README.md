# ElasticSearchと仲良くなりたい

目的:
とあるWebサービスにログインしているお客様の情報を毎日取得し、
日毎のユーザの変化をみたい

例えば・・・
```
全てのユーザさんの中から、10代のユーザで最終ログインが1日以内のユーザ数の遷移を知りたい
```

サンプルデータ
```json
{
    "data": [
        {
            "status": {
                "date": 20160806,   // 今日の日にち
                "age": 10,          // 何十代か
                "last_login": 1,    // 最後にログインしたのは何日以内か
            },
            "data": {
                "account": 10,      // status に該当する人が何人いるか
            }
        },
        ...............
      ]
}
```
ここに書くと長くなるので、サンプルデータはこちら：[elastic_sample.json](https://gist.github.com/cocodrips/18f24c8ffa28cce7beab1c767ba88286)

## まずは導入
[https://www.elastic.co/downloads/elasticsearch](https://www.elastic.co/downloads/elasticsearch)
から ElasticSearchをDL。
最新っぽい2.3.5をDLした

適当な場所に置いて、

```sh
cd lasticsearch-2.3.5
./bin/elasticsearch
```
で、ElasticSearchを起動すると、9200番portに立ち上がる
[localhost:9200](http://localhost:9200/)

[localhost:9200/_nodes/stats/process](http://localhost:9200/_nodes/stats/process)
から、立ち上がったノードの状態とか見れる。
※ノード: ElasticSearch のインスタンスのこと。 この辺りを参考に: [Elasticsearch クラスタ概説](https://gist.github.com/yano3/3f5abc9eba0c1ad6a0508056961b273c)


※このへんに書いてます
[Setup | Elasticsearch Reference [2.3] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html)

## データを入れてみる

ElasticSearchでは、
http://localhost:9200/{index}/{type}/{id}
にjsonをポストすると、
Index > Type のなかにidのデータをつっこめる。
Index, Typeはデータベースのテーブルを分けるみたいな感じに使えばいいと思うのだけど、
どうやって分けるのがいいのか難しい。

今回は以下のようにした。
- Index = サービス名
- Type = "daily_data"

id名は、
後から更新する際に一意にとれる必要があるので、
`{date}_{age}_{last_login}`
というようにデータのキーとなるStatusの値を全部joinしたものにした。

jsonをポストするプログラムを書いてみた in Python2.7
使ったテストデータ:[elastic_sample.json](https://gist.github.com/cocodrips/18f24c8ffa28cce7beab1c767ba88286)
```py
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
```


こんな感じにレスポンスが帰ってきた。
Response
```
20160806_10_3 http://localhost:9200/service_name/daily_data/20160806_10_3 {"status": {"date": 20160806, "age": 10, "last_login": 3}, "@timestamp": "2016-08-06", "data": {"account": 10}}
{"_index":"service_name","_type":"daily_data","_id":"20160806_10_3","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160806_20_3 http://localhost:9200/service_name/daily_data/20160806_20_3 {"status": {"date": 20160806, "age": 20, "last_login": 3}, "@timestamp": "2016-08-06", "data": {"account": 20}}
{"_index":"service_name","_type":"daily_data","_id":"20160806_20_3","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160806_10_1 http://localhost:9200/service_name/daily_data/20160806_10_1 {"status": {"date": 20160806, "age": 10, "last_login": 1}, "@timestamp": "2016-08-06", "data": {"account": 30}}
{"_index":"service_name","_type":"daily_data","_id":"20160806_10_1","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160806_20_1 http://localhost:9200/service_name/daily_data/20160806_20_1 {"status": {"date": 20160806, "age": 20, "last_login": 1}, "@timestamp": "2016-08-06", "data": {"account": 40}}
{"_index":"service_name","_type":"daily_data","_id":"20160806_20_1","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160807_10_3 http://localhost:9200/service_name/daily_data/20160807_10_3 {"status": {"date": 20160807, "age": 10, "last_login": 3}, "@timestamp": "2016-08-07", "data": {"account": 11}}
{"_index":"service_name","_type":"daily_data","_id":"20160807_10_3","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160807_20_3 http://localhost:9200/service_name/daily_data/20160807_20_3 {"status": {"date": 20160807, "age": 20, "last_login": 3}, "@timestamp": "2016-08-07", "data": {"account": 25}}
{"_index":"service_name","_type":"daily_data","_id":"20160807_20_3","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160807_10_1 http://localhost:9200/service_name/daily_data/20160807_10_1 {"status": {"date": 20160807, "age": 10, "last_login": 1}, "@timestamp": "2016-08-07", "data": {"account": 31}}
{"_index":"service_name","_type":"daily_data","_id":"20160807_10_1","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
20160807_20_1 http://localhost:9200/service_name/daily_data/20160807_20_1 {"status": {"date": 20160807, "age": 20, "last_login": 1}, "@timestamp": "2016-08-07", "data": {"account": 41}}
{"_index":"service_name","_type":"daily_data","_id":"20160807_20_1","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}
```

実際に以下にアクセスしてもデータを見られる。
[localhost:9200/service_name/daily_data/20160806_10_3](http://localhost:9200/service_name/daily_data/20160806_10_3)

### postしたデータの型を確認する
アクセスすると、データがどういった型で持たれているかがわかる。
[localhost:9200/service_name/daily_data/_mapping](http://localhost:9200/service_name/daily_data/_mapping)
今回みたいにmappingを特に設定せずにいきなりpostすると、
勝手に判定してmappingしてくれる。

mapping
```json
{
  "service_name": {
    "mappings": {
      "daily_data": {
        "properties": {
          "@timestamp": {
            "type": "date",
            "format": "strict_date_optional_time||epoch_millis"
          },
          "data": {
            "properties": {
              "account": {
                "type": "long"
              }
            }
          },
          "status": {
            "properties": {
              "age": {
                "type": "long"
              },
              "date": {
                "type": "long"
              },
              "last_login": {
                "type": "long"
              }
            }
          }
        }
      }
    }
  }
}
```

[http://localhost:9200/service_name/_search?q=*](http://localhost:9200/service_name/_search?q=*)にアクセスすると、データが全部見える。


### データを消す
データ消したい時は、こんな感じにして消す。
```sh
curl -XDELETE http://localhost:9200/service_name/daily_data/20160806_10_3
```

## データをKibanaに入れてみる

### Kibanaのダウンロード
[Download Kibana Free • Get Started Now | Elastic](https://www.elastic.co/downloads/kibana)

適当なパスに置いて、以下を叩く。
```sh
cd kibana-4.5.4-darwin-x64
./bin/kibana
```
多分5601番に立ち上がる。
[http://0.0.0.0:5601/](http://0.0.0.0:5601/)


### データを可視化する前にKibana設定をする
まずSettingsタブでIndex名を指定する。時間データを入れているキー名もいれておく。(今回は@timestamp)

<img src="https://raw.githubusercontent.com/cocodrips/elasticsearch-lesson/master/images/set-index.png">

あとはこのあたりを参考に
[Kibana 4 BETAファーストインプレッション - Qiita](http://qiita.com/harukasan/items/3737a1cc0bed2facc14e)

<img src="https://raw.githubusercontent.com/cocodrips/elasticsearch-lesson/master/images/date-histgram.png">

## 参考にしたページ
[Fluentd + Elasticsearch + Kibanaで遊んでみた(その1) 〜環境構築から簡単な動作確認まで〜 - カタカタブログ](http://totech.hateblo.jp/entry/2016/01/06/214218)
[Kibana 4 BETAファーストインプレッション - Qiita](http://qiita.com/harukasan/items/3737a1cc0bed2facc14e)
