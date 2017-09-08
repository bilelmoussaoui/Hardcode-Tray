from subprocess import call, Popen, PIPE
from sys import stdout

from HardcodeTray.log import Logger


def progress(count, count_max, time, app_name=""):
    """Used to draw a progress bar."""
    bar_len = 36
    space = 20
    filled_len = int(round(bar_len * count / float(count_max)))

    percents = round(100.0 * count / float(count_max), 1)
    progress_bar = '#' * filled_len + '.' * (bar_len - filled_len)

    stdout.write("\r{0!s}{1!s}".format(app_name,
                                       " " * (abs(len(app_name) - space))))
    stdout.write('[{0}] {1}/{2} {3}% {4:.2f}s\r'.format(progress_bar,
                                                        count, count_max,
                                                        percents, time))
    print("")
    stdout.flush()



def execute(command_list, verbose=True, shell=False, cwd=None):
    """
    Run a command using "Popen".

    Args :
        command_list(list)
        verbose(bool)
    """
    Logger.debug("Executing command: {0}".format(" ".join(command_list)))
    if cwd:
        cmd = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell,
                    cwd=cwd)
    else:
        cmd = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell)

    output, error = cmd.communicate()
    if verbose and error:
        Logger.error(error.decode("utf-8").strip())
    return output


def is_installed(binary):
    """Check if a binary file exists/installed."""
    ink_flag = call(['which', binary], stdout=PIPE, stderr=PIPE)
    return bool(ink_flag == 0)
