pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'carnetgtk')
gnome = import('gnome')

gnome.compile_resources('carnetgtk',
  'carnetgtk.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'carnetgtk.in',
  output: 'carnetgtk',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

carnetgtk_sources = [
  '__init__.py',
  'gi_composites.py',
  'main.py',
  'window.py',
  'ui/adaptive_grid.py',
  'ui/recent_note_list.py',
  'ui/browser_note_list.py',
  'ui/note_list.py',
  'ui/overview.py',
  'ui/overview_toolbar.py',
  'ui/editor_toolbar.py',
  'note_widget.py',
  'libs/html2text.py',
  'server/webdav_sync.py',
  'server/server.py',
  'server/settings_manager.py',
  'server/notes/note_manager.py',
  'server/databases/recent_db_manager.py',
  'server/databases/sync_db.py',
  'server/databases/keyword_db_manager.py',
]

install_data(carnetgtk_sources, install_dir: moduledir)
