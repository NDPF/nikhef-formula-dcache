{%- from "dcache/map.jinja" import dcache with context %}

dcache_packages:
  pkg.installed:
  - names: {{ dcache.pkgs }}

#dcache_service:
#  service.running:
#  - enable: true
#  - name: {{ dcache.service }}
#  - watch:
#    - pkg: dcache_packages

dcache_conf:
  file.managed:
  - name: {{ dcache.conf_dir }}/dcache.conf
  - source: salt://dcache/files/dcache.conf
  - template: jinja
  - user: {{ dcache.user }}
  - group: {{ dcache.group }}
  - mode: 640
#  - watch_in:
#    - service: dcache_service

{%- for key, lines in dcache.gplazma.iteritems() %}
{%- if key == 'default' %}
{%- set name = 'gplazma' %}
{%- else %}
{%- set name = 'gplazma-' + key %}
{%- endif %}

dcache_gplazma_{{ key }}_file:
  file.managed:
  - name: {{ dcache.conf_dir }}/{{ name }}.conf
  - source: salt://dcache/files/gplazma.conf
  - template: jinja
  - user: {{ dcache.user }}
  - group: {{ dcache.group }}
  - mode: 640
  - defaults:
      lines: {{ lines }}
#  - watch_in:
#    - service: dcache_service
{%- endfor %}

{%- for key, data in dcache.kpwd.iteritems() %}
dcache_{{ key }}_kpwd_file:
  file.managed:
  - name: {{ dcache.conf_dir }}/{{ key }}.kpwd
  - source: salt://dcache/files/kpwd
  - template: jinja
  - user: {{ dcache.user }}
  - group: {{ dcache.group }}
  - mode: 640
  - defaults:
      users: {{ data.users }}
#  - watch_in:
#    - service: dcache_service
{%- endfor %}
