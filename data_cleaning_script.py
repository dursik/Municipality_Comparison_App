import argparse
import pickle
from pathlib import Path

import pandas as pd

def find_header_row(excel_file: pd.ExcelFile) -> int:
    preview = excel_file.parse(0, header=None, nrows=20)
    for row in preview.itertuples(index=True):
        if 'IČ (kód)' in row[1:]:
            return row.Index

    return 0


def import_df_all_municipalities(path: Path) -> pd.DataFrame:
    df_of_all_municipalities = pd.ExcelFile(path)
    header_row = find_header_row(df_of_all_municipalities)
    df_of_all_municipalities = df_of_all_municipalities.parse(0, skiprows=header_row)

    return df_of_all_municipalities


def cleanup_df_all_municipalities(df: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    rename_dict = {
        'Rok (kód)':'Year',
        'Období (kód)':'Year',
        'IČ (kód)':'ICO',
        'Obec (název)':'Name',
        'Počet obyvatel (kód)':'Number_of_citizens'}
    new_col_order = ['ICO', 'Name', 'Year', 'Number_of_citizens']

    df_renamed = df.rename(columns=rename_dict)
    df_renamed = df_renamed[new_col_order]
    df_renamed = df_renamed[df_renamed['Year'].isin(years)]
    actually_municipality = [i for i in df_renamed['Name'] if not i.endswith(') ')]
    df_clean = df_renamed.drop(df_renamed[df_renamed['Name'].isin(actually_municipality)].index, axis=0)

    return df_clean


def df_municipalities_pipeline(path: Path, years: list[int]) -> pd.DataFrame:
    df = import_df_all_municipalities(path)
    df_clean = cleanup_df_all_municipalities(df, years)

    return df_clean


def add_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df.insert(1, 'Year', year)

    return df


def import_single_df_FIN(data_dir: Path, year: int) -> pd.DataFrame:
    path = data_dir / f'FINM201_{year}012.csv'
    raw_df_FIN_of_single_year = pd.read_csv(path, sep=';', low_memory=False)

    return raw_df_FIN_of_single_year


def is_not_wanted(column_name: str, wanted_words: list[str]):

    return not any(word in column_name for word in wanted_words)


def cleanup_single_df_FIN(df: pd.DataFrame) -> pd.DataFrame:
    wanted_words = ['ZC_ICO','ZCMMT_ITM','ZU_ROZKZ']
    rename_list = ['ICO','Account','Amount']

    cols_to_drop = [col for col in df.columns if is_not_wanted(col, wanted_words)]
    df_FIN = df.drop(columns=cols_to_drop, errors='ignore')
    df_FIN.columns = rename_list
    df_FIN['Account'] = df_FIN['Account'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_FIN['Amount'] = pd.to_numeric(df_FIN['Amount'], errors='coerce').fillna(0)

    return df_FIN


def pivot_single_df(df: pd.DataFrame) -> pd.DataFrame:
    df_pivoted = df.pivot_table(
        index= 'ICO',
        columns= 'Account',
        values= 'Amount',
        aggfunc= 'sum').fillna(0)
    df_pivoted = df_pivoted.reset_index()

    return df_pivoted


def df_FIN_pipeline(data_dir: Path, year: int) -> pd.DataFrame:
    df = import_single_df_FIN(data_dir, year)
    df_clean = cleanup_single_df_FIN(df)
    df_pivoted = pivot_single_df(df_clean)
    df_FIN = add_year(df_pivoted, year)

    return df_FIN


def import_all_clean_df_FIN(data_dir: Path, years: list[int]) -> pd.DataFrame:
    to_be_concated= [df_FIN_pipeline(data_dir, i) for i in years]
    all_df_FIN = pd.concat(to_be_concated, ignore_index=True)

    return all_df_FIN


def import_single_df_BS(data_dir: Path, year: int) -> pd.DataFrame:
    parts = [1,2]

    to_be_concated = [pd.read_csv(
        data_dir / f'ROZV{i}_{year}012.csv',
        sep=';',
        low_memory=False) for i in parts]
    raw_df_BS = pd.concat(to_be_concated, axis=0)

    return raw_df_BS


def cleanup_single_df_BS(df: pd.DataFrame) -> pd.DataFrame:
    wanted_words = ['ZC_ICO', 'ZC_POLVYK', 'ZC_SYNUC', 'ZU_AONET']
    rename_list = ['ICO','Account','Syn. Account','Amount']

    cols_to_drop = [col for col in df.columns if is_not_wanted(col, wanted_words)]
    df_BS = df.drop(columns=cols_to_drop, errors='ignore')
    df_BS.columns = rename_list

    df_BS['Account'] = df_BS['Account'] + ' = ' + df_BS['Syn. Account']
    df_BS = df_BS.drop(columns= 'Syn. Account')
    df_BS['Amount'] = pd.to_numeric(df_BS['Amount'], errors='coerce').fillna(0)

    return df_BS


def df_BS_pipeline(data_dir: Path, year: int) -> pd.DataFrame:
    df = import_single_df_BS(data_dir, year)
    df_clean = cleanup_single_df_BS(df)
    df_pivoted = pivot_single_df(df_clean)
    df_BS = add_year(df_pivoted, year)

    return df_BS


def import_all_clean_df_BS(data_dir: Path, years: list[int]) -> pd.DataFrame:
    to_be_concated= [df_BS_pipeline(data_dir, i) for i in years]
    all_df_BS = pd.concat(to_be_concated, ignore_index=True)

    return all_df_BS


def merge_all_dfs(data_dir: Path, municipalities_file: Path, years: list[int]) -> pd.DataFrame:
    names_df = df_municipalities_pipeline(municipalities_file, years)
    FIN_df = import_all_clean_df_FIN(data_dir, years)
    BS_df = import_all_clean_df_BS(data_dir, years)

    merged_df = names_df.merge(FIN_df, how='left', on=['ICO','Year'])
    merged_df = merged_df.merge(BS_df, how='left', on=['ICO', 'Year'])

    return merged_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Sloučí výkazy FIN 2-12 M, rozvahy a počty obyvatel do data.pkl.')
    parser.add_argument('--year', type=int, required=True,
                        help='poslední analyzovaný rok, čtyřmístně (např. 2025)')
    parser.add_argument('--data-dir', type=Path, required=True,
                        help='složka se soubory FINM201_*.csv a ROZV*_*.csv')
    parser.add_argument('--municipalities-file', type=Path, default=None,
                        help='export počtu obyvatel z portálu MONITOR '
                             '(výchozí: <data-dir>/FINM_PV.xlsx)')
    parser.add_argument('--years-back', type=int, default=6,
                        help='kolik let zpět zahrnout (výchozí: 6)')
    parser.add_argument('--output', type=Path, default=Path('data.pkl'),
                        help='výstupní pickle soubor (výchozí: data.pkl)')

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.year < 1000:
        raise SystemExit('--year musí být čtyřmístný rok, např. 2025')
    if args.years_back < 0:
        raise SystemExit('--years-back nesmí být záporné')
    if not args.data_dir.is_dir():
        raise SystemExit(f'Složka {args.data_dir} neexistuje')

    municipalities_file = args.municipalities_file or args.data_dir / 'FINM_PV.xlsx'
    if not municipalities_file.is_file():
        raise SystemExit(f'Soubor {municipalities_file} neexistuje')

    years = list(range(args.year - args.years_back, args.year + 1))
    print(f'Zpracovávám roky {years[0]}-{years[-1]} ze složky {args.data_dir}')

    merged_df = merge_all_dfs(args.data_dir, municipalities_file, years).round(2)

    with open(args.output, 'wb') as f:
        pickle.dump(merged_df, f)

    print(f'Uloženo {len(merged_df)} řádků do {args.output}')


if __name__ == '__main__':
    main()
