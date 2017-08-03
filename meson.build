project('hardcode-tray',
  version: '4.1',
  meson_version: '>= 0.40.0',
  license: 'GPL-3.0'
)

dependency('gobject-introspection-1.0')
dependency('gtk+-3.0')

i18n = import('i18n')
python = import('python3')

PYTHON_DIR = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
LOCALE_DIR = join_paths(get_option('prefix'), get_option('datadir'), 'locale')

# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', DATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PACKAGE', meson.project_name())
conf.set('VERSION', meson.project_version())

subdir('data')
subdir('po')

install_subdir(
  'HardcodeTray',
  install_dir: PYTHON_DIR
)

configure_file(
  input: 'const.py.in',
  output: 'const.py',
  configuration: conf,
  install_dir: join_paths(PYTHON_DIR, 'HardcodeTray')
)

install_subdir(
  'license',
  install_dir: DATA_DIR
)

configure_file(
  input: meson.project_name() + '.py.in',
  output: meson.project_name(),
  configuration: conf,
  install_dir: join_paths(get_option('prefix'), 'bin')
)
