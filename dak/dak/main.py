import argparse
import signal
import sys

from dak import DAK


def main():
    parser = argparse.ArgumentParser(description='Digital Autopoietic Kernel')
    parser.add_argument('--mode', choices=['headless', 'repl', 'tui', 'api', 'chat'],
                        default='headless',
                        help='Interaction mode (default: headless)')
    parser.add_argument('--usf', action='store_true',
                        help='Enable USF transformer (simplicial intelligence engine)')
    args = parser.parse_args()

    dak = DAK()
    if args.usf:
        dak.usf_enabled = True
        if dak.usf_transformer is None:
            dak._init_usf()

    def handle_signal(sig, frame):
        print('\n[main] Signal received, shutting down...')
        dak.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if args.mode == 'headless':
        print('DAK running in headless mode. Ctrl+C to stop.')
        dak.run()
    elif args.mode == 'repl':
        from dak.interact.repl import DAKREPL
        t = dak.run_async()
        try:
            DAKREPL(dak).cmdloop()
        finally:
            dak.stop()
            t.join()
    elif args.mode == 'tui':
        from dak.interact.tui import main as tui_main
        tui_main()
    elif args.mode == 'api':
        from dak.interact.api import main as api_main
        api_main()
    elif args.mode == 'chat':
        from dak.interact.chat import main as chat_main
        chat_main()


def usf_main():
    import dak.config.settings as settings
    settings.USF_ENABLED = True
    sys.argv = [a for a in sys.argv if 'dak-usf' not in a]
    if '--usf' not in sys.argv:
        sys.argv.insert(1, '--usf')
    if '--mode' not in sys.argv:
        sys.argv.extend(['--mode', 'chat'])
    main()


if __name__ == '__main__':
    main()
