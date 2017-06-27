{%- from "dcache/map.jinja" import dcache with context %}

dcache_packages:
  pkg.installed:
  - names: {{ dcache.pkgs }}

dcache_service:
  service.running:
  - enable: true
  - name: {{ dcache.service }}
  - watch:
    - pkg: dcache_packages

dcache_conf:
  file.managed:
  - name: {{ dcache.conf_dir }}/dcache.conf
  - source: salt://dcache/files/dcache.conf
  - template: jinja
  - user: {{ dcache.user }}
  - group: {{ dcache.group }}
  - mode: 640
  - watch_in:
    - service: dcache_service

dcache_layout_conf:
  file.managed:
  - name: {{ dcache.conf_dir }}/layouts/{{ dcache.layout }}.conf
  - source: salt://dcache/files/layout.conf
  - template: jinja
  - user: {{ dcache.user }}
  - group: {{ dcache.group }}
  - mode: 640
  - watch_in:
    - service: dcache_service

{%- if dcache.authorized_keys2 is defined and dcache.authorized_keys2|length > 1 %}
dcache_authorized_keys2:
  file.managed:
  - name: {{ dcache.conf_dir }}/admin/authorized_keys2
  - source: salt://dcache/files/authorized_keys2
  - template: jinja
  - user: {{ dcache.user }}
  - group: {{ dcache.group }}
  - mode: 640
  - defaults:
      users: {{ dcache.authorized_keys2 }}
  - watch_in:
    - service: dcache_service
{%- endif %}

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
  - watch_in:
    - service: dcache_service
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
  - watch_in:
    - service: dcache_service
{%- endfor %}

{%- for name in dcache.databases %}
dcache_setup_database_{{ name }}:
  cmd.run:
  - name: dcache database update
  - onchanges:
{%- for db in dcache.databases %}
      - postgres_database: postgresql_database_localhost_{{ db }}
{%- endfor %}
  - watch_in:
    - service: dcache_service
{%- endfor %}
