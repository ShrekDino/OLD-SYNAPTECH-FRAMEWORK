import threading
import time

from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Center
from rich import box

from dak import DAK


def _make_state_table(dak) -> Table:
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column('Metric', style='cyan')
    table.add_column('Value', style='green')
    table.add_row('F', f'{dak.F:.4f} nats')
    table.add_row('H_env', f'{dak.H_env:.4f} bits/s')
    table.add_row('S_gen', f'{dak.S_gen:.6f} nats/s')
    table.add_row('Szilard ratio', f'{dak.szilard_ratio:.4f}')
    table.add_row('δ', f'{dak.delta:.6f}')
    table.add_row('I(μ)', f'{dak.mutual_info:.4f} nats')
    table.add_row('Tick', str(dak.tick_count))
    return table


def _make_phase_panel(dak) -> Panel:
    phase = dak.dqfr.phase.value
    t_in = dak.dqfr.time_in_phase
    utility = dak.dqfr.utility
    status = Text.assemble(
        ('PHASE: ', 'bold cyan'),
        (f'{phase}', 'bold yellow' if phase == 'SAMPLING' else 'bold blue'),
        ('\nTime in phase: ', 'cyan'),
        (f'{t_in:.1f}s', 'white'),
        ('\nUtility: ', 'cyan'),
        (f'{utility:.4f}', 'green' if utility > 0 else 'red'),
    )
    return Panel(status, title='DQFR', border_style='bright_blue')


def _make_sensor_panel(dak) -> Panel:
    sensors = dak.telemetry.read_all()
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column('Sensor', style='dim')
    table.add_column('Value')
    for k in ['cpu_percent', 'mem_percent', 'load_1min', 'processes']:
        if k in sensors:
            v = sensors[k]
            if isinstance(v, float):
                table.add_row(k, f'{v:.2f}')
            else:
                table.add_row(k, str(v))
    return Panel(table, title='Sensors', border_style='green')


def _make_mu_panel(dak) -> Panel:
    mu = dak.state.read()
    mu_norm = float(  # noqa: F841
        sum(x * x for x in mu) ** 0.5
    )
    hist = dak.state.history
    if len(hist) > 1:
        diffs = [abs(hist[-i] - hist[-i - 1]).sum() for i in range(1, min(5, len(hist)))]
        flux = sum(diffs) / len(diffs)
    else:
        flux = 0.0
    info = Text.assemble(
        ('μ norm: ', 'cyan'),
        (f'{mu_norm:.4f}', 'white'),
        ('\nμ flux: ', 'cyan'),
        (f'{flux:.6f}', 'white'),
        ('\nμ dim: ', 'cyan'),
        (f'{len(mu)}', 'white'),
    )
    return Panel(info, title='Internal State', border_style='magenta')


def _build_layout(dak) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name='header', size=3),
        Layout(name='body'),
        Layout(name='footer', size=1),
    )
    layout['body'].split_row(
        Layout(name='left'),
        Layout(name='right'),
    )
    layout['left'].split(
        Layout(name='phase_panel'),
        Layout(name='mu_panel'),
    )
    layout['right'].split(
        Layout(name='state_panel'),
        Layout(name='sensor_panel'),
    )
    return layout


def tui_loop(dak, live: Live, layout: Layout, stop_event):
    while not stop_event.is_set():
        layout['header'].update(
            Panel(
                Center(Text('Digital Autopoietic Kernel (DAK)', style='bold bright_cyan')),
                border_style='bright_cyan',
            )
        )
        layout['phase_panel'].update(_make_phase_panel(dak))
        layout['mu_panel'].update(_make_mu_panel(dak))
        layout['state_panel'].update(Panel(_make_state_table(dak), title='Thermodynamics', border_style='yellow'))
        layout['sensor_panel'].update(_make_sensor_panel(dak))
        layout['footer'].update(
            Center(Text('q: quit  r: refresh  (commands at bottom)', style='dim'))
        )
        time.sleep(0.25)


def main():
    print('Booting DAK kernel for TUI...')
    dak = DAK()
    t = dak.run_async()
    stop_event = threading.Event()

    layout = _build_layout(dak)

    try:
        with Live(layout, refresh_per_second=4, screen=True) as live:
            tui_thread = threading.Thread(
                target=tui_loop, args=(dak, live, layout, stop_event), daemon=True
            )
            tui_thread.start()
            while True:
                import sys
                import tty
                import termios

                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                if ch == 'q':
                    break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stop_event.set()
        dak.stop()
        t.join()


if __name__ == '__main__':
    main()
