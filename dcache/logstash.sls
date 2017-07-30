{%- from "dcache/map.jinja" import dcache with context %}

{%- if dcache.logstash.enabled|default(False) %}
dcache_logstash_conf:
  file.managed:
  - name: {{ dcache.logstash_dir }}/conf.d/dcache-billing.conf
  - source: salt://dcache/files/logstash/dcache-billing.conf
  - template: jinja
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: logstash_packages
  - watch_in:
    - service: logstash_service

dcache_logstash_patterns:
  file.managed:
  - name: {{ dcache.logstash_dir }}/patterns/dcache-billing
  - source: salt://dcache/files/logstash/dcache-billing
  - makedirs: true
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: logstash_packages
  - watch_in:
    - service: logstash_service
{%- endif %}
