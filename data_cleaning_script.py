import pandas as pd
import pickle

year = int(input('Enter year:'))
print('Got the input!')

years_to_analyze = 6
latest_year = year - years_to_analyze
all_needed_years = range(latest_year, year+1)
all_needed_years_full = [(2000+i) for i in all_needed_years]


def import_df_all_municipalities() -> pd.DataFrame:
    path = r"/home/hbrvk/projects/old/MONITOR/municipality_comp/data/FINM_PV.xlsx"
    
    df_of_all_municipalities = pd.ExcelFile(path)
    df_of_all_municipalities = df_of_all_municipalities.parse(0)
    
    return df_of_all_municipalities


def cleanup_df_all_municipalities(df: pd.DataFrame) -> pd.DataFrame:
    rename_dict = {
        'Rok (kód)':'Year',
        'IČ (kód)':'ICO',
        'Obec (název)':'Name',
        'Počet obyvatel (kód)':'Number_of_citizens'}
    new_col_order = ['ICO', 'Name', 'Year', 'Number_of_citizens']

    df_renamed = df.rename(columns=rename_dict)
    df_renamed = df_renamed[new_col_order]
    df_renamed = df_renamed[df_renamed['Year'].isin(all_needed_years_full)]
    actually_municipality = [i for i in df_renamed['Name'] if not i.endswith(') ')]
    df_clean = df_renamed.drop(df_renamed[df_renamed['Name'].isin(actually_municipality)].index, axis=0)

    return df_clean


def df_municipalities_pipeline() -> pd.DataFrame:
    df = import_df_all_municipalities()
    df_clean = cleanup_df_all_municipalities(df)

    return df_clean


def add_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df.insert(1, 'Year', int(f'20{year}'))

    return df


def import_single_df_FIN(year: int) -> pd.DataFrame:
    path = rf'/home/hbrvk/projects/old/MONITOR/municipality_comp/data/FINM201_20{year}012.csv'
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


def df_FIN_pipeline(year: int) -> pd.DataFrame:
    df = import_single_df_FIN(year)
    df_clean = cleanup_single_df_FIN(df)
    df_pivoted = pivot_single_df(df_clean)
    df_FIN = add_year(df_pivoted, year)

    return df_FIN


def import_all_clean_df_FIN() -> pd.DataFrame:    
    to_be_concated= [df_FIN_pipeline(i) for i in all_needed_years]    
    all_df_FIN = pd.concat(to_be_concated, ignore_index=True)

    return all_df_FIN


def import_single_df_BS(year: int) -> pd.DataFrame:
    base_path = r"/home/hbrvk/projects/old/MONITOR/municipality_comp/data/"
    parts = [1,2]

    to_be_concated = [pd.read_csv(
        f"{base_path}ROZV{i}_20{year}012.csv", 
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


def df_BS_pipeline(year: int) -> pd.DataFrame:
    df = import_single_df_BS(year)
    df_clean = cleanup_single_df_BS(df)
    df_pivoted = pivot_single_df(df_clean)
    df_BS = add_year(df_pivoted, year)

    return df_BS


def import_all_clean_df_BS() -> pd.DataFrame:    
    to_be_concated= [df_BS_pipeline(i) for i in all_needed_years]    
    all_df_BS = pd.concat(to_be_concated, ignore_index=True)

    return all_df_BS


def merge_all_dfs() -> pd.DataFrame:
    names_df = df_municipalities_pipeline()
    FIN_df = import_all_clean_df_FIN()
    BS_df = import_all_clean_df_BS()

    merged_df = names_df.merge(FIN_df, how='left', on=['ICO','Year'])
    merged_df = merged_df.merge(BS_df, how='left', on=['ICO', 'Year'])

    return merged_df


with open("data.pkl", "wb") as f:
    pickle.dump(merge_all_dfs().round(2), f)

