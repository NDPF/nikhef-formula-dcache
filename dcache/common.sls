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

{%- if dcache.authorized_keys2 is defined %}
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

{%- for key, lines in dcache.get('gplazma', {}).iteritems() %}
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

{%- for key, data in dcache.get('kpwd', {}).iteritems() %}
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

{%- for name in dcache.get('databases', []) %}
dcache_setup_database_{{ name }}:
  cmd.run:
  - name: dcache database update
  - require:
    - pkg: dcache_packages
  - onchanges:
{%- for db in dcache.databases %}
      - postgres_database: postgresql_database_localhost_{{ db }}
{%- endfor %}
  - watch_in:
    - service: dcache_service
{%- endfor %}

{%- if dcache.nfs_exports is defined %}
dcache_nfs_exports:
  file.managed:
  - name: /etc/exports
  - source: salt://dcache/files/exports
  - template: jinja
  - user: root
  - group: root
  - mode: 644
{%- endif %}

{%- if dcache.pool_setup %}
{%- for pool in dcache.get('pools', []) %}
dcache_setup_pool_{{ pool.name }}:
  cmd.run:
  - name: dcache pool create {{ pool.dir }}/{{ pool.name }} {{ pool.name }} {{ pool.name }}Domain
  - onlyif: "test `test -d '{{ pool.dir }}/{{ pool.name }}' >/dev/null;echo $?` -eq 1"
  - require:
    - pkg: dcache_packages
{%- endfor %}
{%- endif %}
