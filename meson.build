project('hardcode-tray',
  version: '4.0'
)

i18n = import('i18n')

script_dir = '/opt/Hardcode-Tray/'

subdir('data')
subdir('po')

install_subdir(
  'src',
  install_dir: script_dir
)
install_subdir(
  'license',
  install_dir: script_dir
)
install_data(
  meson.project_name() + '.py',
  install_dir: script_dir
)
install_data(
  meson.project_name(),
  install_dir: join_paths(get_option('prefix'), 'bin')
)
