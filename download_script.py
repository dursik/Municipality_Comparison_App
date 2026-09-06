import argparse
import shutil
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

BASE_URL = 'https://monitor.statnipokladna.gov.cz/data'
DATASETS = (
    ('FINM', 'FinM', ('FINM201_{year}012.csv',)),
    ('ROZV', 'Rozvaha', ('ROZV1_{year}012.csv', 'ROZV2_{year}012.csv')),
)


def format_size(size: int) -> str:

    return f'{size / 1024 / 1024:.0f} MB'


def download_file(url: str, target: Path) -> None:
    partial = target.with_suffix(target.suffix + '.part')

    with urllib.request.urlopen(url) as response, open(partial, 'wb') as f:
        shutil.copyfileobj(response, f)

    partial.replace(target)


def extract_members(archive: Path, members: list[str], data_dir: Path) -> None:
    with zipfile.ZipFile(archive) as opened_archive:
        available = set(opened_archive.namelist())
        missing = [member for member in members if member not in available]

        if missing:
            raise SystemExit(f'V archivu {archive.name} chybí: {", ".join(missing)}')

        for member in members:
            opened_archive.extract(member, data_dir)


def download_statements(data_dir: Path, years: list[int], overwrite: bool) -> list[str]:
    failed = []

    for year in years:
        for dataset_id, dataset_dir, member_patterns in DATASETS:
            members = [pattern.format(year=year) for pattern in member_patterns]
            targets = [data_dir / member for member in members]

            if not overwrite and all(target.is_file() for target in targets):
                print(f'{year} {dataset_id}: přeskakuji, soubory už existují')
                continue

            url = f'{BASE_URL}/extrakty/csv/{dataset_dir}/{year}_12_Data_CSUIS_{dataset_id}.zip'
            archive = data_dir / f'{year}_{dataset_id}.zip'
            print(f'{year} {dataset_id}: stahuji {url}')

            try:
                download_file(url, archive)
            except urllib.error.HTTPError as error:
                print(f'{year} {dataset_id}: nedostupné ({error.code}), pokračuji dál')
                failed.append(f'{year} {dataset_id}')
                continue

            extract_members(archive, members, data_dir)
            archive.unlink()

            extracted = sum(target.stat().st_size for target in targets)
            print(f'{year} {dataset_id}: rozbaleno {len(members)} souborů, {format_size(extracted)}')

    return failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Stáhne výkazy FIN 2-12 M a rozvahy z portálu MONITOR.')
    parser.add_argument('--year', type=int, required=True,
                        help='poslední analyzovaný rok, čtyřmístně (např. 2025)')
    parser.add_argument('--data-dir', type=Path, default=Path('data'),
                        help='cílová složka (výchozí: data)')
    parser.add_argument('--years-back', type=int, default=6,
                        help='kolik let zpět stáhnout (výchozí: 6)')
    parser.add_argument('--overwrite', action='store_true',
                        help='stáhnout znovu i soubory, které už existují')

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.year < 1000:
        raise SystemExit('--year musí být čtyřmístný rok, např. 2025')
    if args.years_back < 0:
        raise SystemExit('--years-back nesmí být záporné')

    args.data_dir.mkdir(parents=True, exist_ok=True)
    years = list(range(args.year - args.years_back, args.year + 1))
    print(f'Stahuji roky {years[0]}-{years[-1]} do složky {args.data_dir}')

    failed = download_statements(args.data_dir, years, args.overwrite)

    if failed:
        raise SystemExit(f'Nepodařilo se stáhnout: {", ".join(failed)}')

    print(f'Hotovo, data jsou ve složce {args.data_dir}')


if __name__ == '__main__':
    main()
