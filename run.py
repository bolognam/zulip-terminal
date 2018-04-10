#!/usr/bin/env python3
import argparse
import sys
from os import environ, path

from zulipterminal.core import Controller


def save_stdout():
    """Save shell screen."""
    sys.stdout.write("\033[?1049h\033[H")


def restore_stdout():
    """Restore saved shell screen."""
    sys.stdout.write("\033[?1049l")


def parse_args():
    description = '''
        Starts Zulip-Terminal.
        '''
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter_class)

    parser.add_argument('--config-file', '-c',
                        action='store',
                        help='config file downloaded from your zulip\
                             organization.(e.g. ~/zuliprc)')
    parser.add_argument('--theme', '-t',
                        default='default',
                        help='choose color theme. (e.g. blue, light)')
    # debug mode
    parser.add_argument("-d",
                        "--debug",
                        action="store_true",
                        help="Start zulip terminal in debug mode.")

    parser.add_argument('--profile', dest='profile',
                        action="store_true",
                        default=False, help='Profile runtime.')

    args = parser.parse_args()
    return args


def get_config_files():
    zulip_extension = '/zulip/zulip.ini'
    zterm_extension = '/zulip/zterm.ini'
    dirs = environ.get('XDG_CONFIG_DIRS')
    if dirs is None:
        dirs = '~/.config'
        config_dir = path.expanduser(dirs)
        if not path.exists(config_dir):
            sys.exit("Error: Cannot find config directory: {}".format(config_dir))

    dirs_split = dirs.split(':')
    config_dir = None
    for d in dirs_split:
        zulip_path = path.expanduser(d + zulip_extension)
        if path.exists(zulip_path):
            config_dir = path.expanduser(d)
            break

    if config_dir is None:
        dirs_str = dirs_split[0] + '/zulip/'
        for i in range(1, len(dirs_split)):
            dirs_str += ' or ' + dirs_split[i] + '/zulip/'

        sys.exit("Error: cannot find zulip.ini in {}".format(dirs_str))

    return config_dir + zulip_extension, config_dir + zterm_extension


def main():
    """
    Launch Zulip Terminal.
    """
    args = parse_args()
    if args.debug:
        save_stdout()
    if args.profile:
        import cProfile
        prof = cProfile.Profile()
        prof.enable()

    try:
        Controller(args.config_file, args.theme).main()
    except Exception:
        # A unexpected exception occurred, open the debugger in debug mode
        if args.debug:
            import pudb
            pudb.post_mortem()
    finally:
        if args.debug:
            restore_stdout()

        if args.profile:
            prof.disable()
            prof.dump_stats("/tmp/profile.data")
            print("Profile data saved to /tmp/profile.data")
            print("You can visualize it using e.g."
                  "`snakeviz /tmp/profile.data`")

        print("\nThanks for using the Zulip-Terminal interface.\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
