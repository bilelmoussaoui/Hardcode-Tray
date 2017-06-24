project('hardcode-tray',
  version: '4.1'
)

i18n = import('i18n')
python = find_program('python3')
message('Getting python install dir')
r = run_command(python, '-c', 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')
if r.returncode() != 0
    error('Cannot find python install dir')
endif
python_dir = r.stdout().strip()

script_dir = '/opt/Hardcode-Tray/'

subdir('data')
subdir('po')

install_subdir(
  'HardcodeTray',
  install_dir: python_dir
)

install_subdir(
  'license',
  install_dir: script_dir
)
# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', script_dir)
conf.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
conf.set('PACKAGE', meson.project_name())
conf.set('VERSION', meson.project_version())

configure_file(
  input: meson.project_name() + '.py.in',
  output: meson.project_name(),
  configuration: conf,
  install_dir: join_paths(get_option('prefix'), 'bin')
)
