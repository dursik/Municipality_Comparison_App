import argparse
import subprocess
import sys
from pathlib import Path

APP_FILE = 'app.py'
DATA_FILE = 'points.pkl'
SECRETS_FILE = Path('.streamlit') / 'secrets.toml'
PIPELINE_HINT = ('download_script.py, data_cleaning_script.py, '
                 'ratios_script.py a distributions.py')


def check_prerequisites(project_dir: Path) -> None:
    if not (project_dir / APP_FILE).is_file():
        raise SystemExit(f'Ve složce {project_dir} chybí {APP_FILE}')

    if not (project_dir / DATA_FILE).is_file():
        raise SystemExit(f'Chybí {DATA_FILE}, nejdřív spusť {PIPELINE_HINT}')

    if not (project_dir / SECRETS_FILE).is_file():
        print(f'Upozornění: chybí {SECRETS_FILE}, '
              'aplikace se zastaví na přihlašovací obrazovce', flush=True)


def build_command(project_dir: Path, port: int, headless: bool) -> list[str]:
    command = [sys.executable, '-m', 'streamlit', 'run',
               str(project_dir / APP_FILE),
               '--server.port', str(port)]

    if headless:
        command += ['--server.headless', 'true']

    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Spustí webové rozhraní aplikace ve Streamlitu.')
    parser.add_argument('--port', type=int, default=8501,
                        help='port webového serveru (výchozí: 8501)')
    parser.add_argument('--headless', action='store_true',
                        help='neotevírat prohlížeč a přeskočit úvodní dotaz Streamlitu')

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not 1 <= args.port <= 65535:
        raise SystemExit('--port musí být mezi 1 a 65535')

    project_dir = Path(__file__).resolve().parent
    check_prerequisites(project_dir)

    print(f'Spouštím {APP_FILE} na http://localhost:{args.port}', flush=True)

    try:
        exit_code = subprocess.call(build_command(project_dir, args.port, args.headless))
    except FileNotFoundError:
        raise SystemExit('Streamlit není nainstalovaný, spusť pip install -r requirements.txt')
    except KeyboardInterrupt:
        print('\nUkončeno')
        return

    raise SystemExit(exit_code)


if __name__ == '__main__':
    main()
