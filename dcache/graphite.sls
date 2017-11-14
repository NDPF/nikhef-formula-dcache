{%- from "dcache/map.jinja" import dcache with context %}

{%- if dcache.graphite_monitoring|default(False) %}
dcache_graphite_metrics_packages:
  pkg.installed:
  - names:
      - pexpect

dcache_graphite_metrics:
  file.managed:
  - name: /opt/metrics/dcache-metrics.py
  - source: salt://dcache/files/dcache-metrics.py
  - makedirs: true
  - template: jinja
  - user: root
  - group: root
  - mode: 755
  - require:
    - pkg: dcache_graphite_metrics_packages

dcache_graphite_metrics_cronjob:
  crontab.crond:
  - name: dcache-metrics
  - minute: '*/1'
  - printdate: false
  - cmd: /opt/metrics/dcache-metrics.py
  - require:
    - file: dcache_graphite_metrics
{%- endif %}
