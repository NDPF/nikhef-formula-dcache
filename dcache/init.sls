{%- if pillar.dcache is defined %}
include:
- dcache.server

{%- if pillar.dcache.logstash is defined %}
- dcache.logstash
{%- endif %}

{%- endif %}
