{%- if pillar.dcache is defined %}
include:
- dcache.server

{%- if pillar.dcache.logstash is defined %}
- dcache.logstash
{%- endif %}

{%- if pillar.dcache.graphite_monitoring is defined %}
- dcache.graphite
{%- endif %}

{%- endif %}
