## This is project for installing and configuring monitoring infrastructure.
GET example-index/_search
{
    "query" : { "query_string" : {"query" : "*"} }
  }
  
GET _cat/indices?v

GET _cluster/health?pretty


logstash input plugins
```
https://www.elastic.co/guide/en/logstash/current/codec-plugins.html
```
logstash filter plugins
```
https://www.elastic.co/guide/en/logstash/current/filter-plugins.html
```
logstash filter plugins
```
https://www.elastic.co/guide/en/logstash/current/output-plugins.html
```
Logstash patterns
```
https://github.com/logstash-plugins/logstash-patterns-core
``` 