import pandas as pd
import pickle

with open("data.pkl", "rb") as f:
    data = pickle.load(f)

year = int(input("Input year:"))

def add_a_category(df: pd.DataFrame) -> pd.DataFrame:
    category: list[int|float] = [0, 100, 200, 500, 1000, 
                                2000, 5000, 10000, 20000, 
                                50000, 100000, 1000000, float('inf')]
    text = [
    '0 to 100',
    '101 to 200',
    '201 to 500',
    '501 to 1 000',
    '1 001 to 2 000',
    '2 001 to 5 000',
    '5 001 to 10 000',
    '10 001 to 20 000',
    '20 001 to 50 000',
    '50 001 to 100 000',
    '100 001 to 1 000 000',
    'above 1 000 000']
    
    new_category_column = pd.cut(df['Number_of_citizens'], bins=category,
                                 labels=text, right=True, include_lowest=True)
    df.insert(2, 'Category', new_category_column)

    return df


def appending_ratio_logic(col_name: str,
                          wanted_accounts: tuple[str,...],
                          not_wanted_accounts: tuple[str,...]):
    
    return col_name.startswith(wanted_accounts) and not col_name.startswith(not_wanted_accounts)


def earnings_per_citizen_ratio(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts = ('1','2','3','4')
    not_wanted_accounts = ('4132','4133','4134','4135','4136','4137','4138','4139')

    all_computational_accounts = [i for i in df.columns 
                                  if appending_ratio_logic(i,wanted_accounts,not_wanted_accounts)]
    df['Celkové_příjmy'] = df[all_computational_accounts].sum(axis=1)
    df['Celkové_příjmy_na_jednoho_obyvatele'] = df['Celkové_příjmy'] / df['Number_of_citizens']

    return df


def tax_earnings_per_citizen(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts = ('1',)
    not_wanted_accounts = ()

    all_computational_accounts = [i for i in df.columns 
                                  if appending_ratio_logic(i,wanted_accounts,not_wanted_accounts)]
    df['Daňové_příjmy'] = df[all_computational_accounts].sum(axis=1)
    df['Daňové_příjmy_na_jednoho_obyvatele'] = df['Daňové_příjmy'] / df['Number_of_citizens']

    return df


def financial_independency(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts_A = ('2','31','13','15')
    not_wanted_accounts_A = ('214','24','3114','3115','3116','3117','3118','3119','138',"312")
    
    all_own_earnings_accounts = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_A, not_wanted_accounts_A)]
    df['Vlastní_příjmy'] =  df[all_own_earnings_accounts].sum(axis=1) - df['4131']
    
    wanted_accounts_B = ('2','31','1','41')
    not_wanted_accounts_B = ('214','1122', "4131","4133","4134","4135","4136","4137","4138","4139", "312",'24')
    
    all_clean_earnings_accounts = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_B, not_wanted_accounts_B)]
    df['Čisté_běžné_příjmy'] =  df[all_clean_earnings_accounts].sum(axis=1)
    df['Finanční_nezávislost'] = (df['Vlastní_příjmy'] / df['Čisté_běžné_příjmy'])*100

    return df


def financial_self_sufficiency(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts_A = ('5',)
    not_wanted_accounts_A = ('5141','5144','5146','530','534','535','537',
                             '538','539','5903','56','5341','5142','5149')
    
    all_computational_accounts_A = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_A, not_wanted_accounts_A)]
    
    wanted_accounts_B = ('1122','3122','5363','24','3121')
    not_wanted_accounts_B = ()
    
    all_computational_accounts_B = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_B, not_wanted_accounts_B)]
    df['Čisté_běžné_výdaje']= (df[all_computational_accounts_A].sum(axis=1) - 
                                   df[all_computational_accounts_B].sum(axis = 1))
    df['Finanční_soběstačnost'] = (df['Vlastní_příjmy'] / df['Čisté_běžné_výdaje']) * 100

    return df


def liabilities_to_balance(df: pd.DataFrame) -> pd.DataFrame:
    
    wanted_accounts_A = ('1','2','41')
    not_wanted_accounts_A = ('4133','4134','4135','4136','4137','4138','4139')
    
    all_computational_accounts_A = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_A, not_wanted_accounts_A)]
    
    wanted_accounts_B = ('5',)
    not_wanted_accounts_B = ('5141','5144','530','5311','5312','5313','5314','5315','5316','5317','5318',
                             '5342','5343','5344','5345','5346','5347','5348','5349','535','537','538','539')
    
    all_computational_accounts_B = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_B, not_wanted_accounts_B)]


    df['Běžné_příjmy'] = df[all_computational_accounts_A].sum(axis=1)
    df['Celkové_závazky'] = df['D. = -'] - df[['D.I. = -', 'D.III.36. = 384','D.III.35. = 383']].sum(axis=1)
    df['Běžné_výdaje'] = df[all_computational_accounts_B].sum(axis=1)
    df['Výše_dluhu_k_saldu_běžného_rozpočtu'] = df['Celkové_závazky'] / (df['Běžné_příjmy'] - df['Běžné_výdaje'])

    return df


def liabilities_to_surplus(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts_A = ('3',)
    not_wanted_accounts_A = ("3121",)
    
    all_computational_accounts_A = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_A, not_wanted_accounts_A)]
    
    df['PPE_prodáno']= df[all_computational_accounts_A].sum(axis=1)
    df['Krytí_dluhu_provozním_přebytkem'] = df['Celkové_závazky'] / (df['Čisté_běžné_příjmy'] - df['Čisté_běžné_výdaje'] - df['PPE_prodáno'])

    return df


def capital_expenses_coverage(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts_A = ('6',)
    not_wanted_accounts_A = ()
    
    all_computational_accounts_A = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_A, not_wanted_accounts_A)]
    
    df['Kapitálové_výdaje'] = df[all_computational_accounts_A].sum(axis=1)
    df['Kapitálové_výdaje'] = df['Kapitálové_výdaje'].replace(0,1)
    
    wanted_accounts_B = ('42',)
    not_wanted_accounts_B = ()
    
    all_computational_accounts_B = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts_B, not_wanted_accounts_B)]
    
    df['Investiční_kapitálové_příjmy'] = df[all_computational_accounts_B].sum(axis=1)
    df['Krytí_kapitálových_výdajů_investičními_transfery'] = (df['Investiční_kapitálové_příjmy'] / df['Kapitálové_výdaje'])*100

    return df


def total_debt(df: pd.DataFrame) -> pd.DataFrame:
    wanted_accounts = ('D.III.1. = 281', 'D.III.2. = 282', 'D.III.3. = 283', 'D.III.4. = 289',
                      'D.III.6. = 322', 'D.III.9. = 326', 'D.III.27. = 362', 'D.II.1. = 451',
                     'D.II.2. = 452', 'D.II.3. = 453', 'D.II.5. = 456','D.II.6. = 457', 'D.II.7. = 459')
    not_wanted_accounts = ()

    all_computational_accounts = [i for i in df.columns
                                  if appending_ratio_logic(i,wanted_accounts, not_wanted_accounts)]
    df['Dluh'] = df[all_computational_accounts].sum(axis=1)

    return df


def add_moving_average_income(df: pd.DataFrame) -> pd.DataFrame:
    all_years = sorted(df['Year'].unique())
    target_years = all_years[-2:]
    
    results_list: list[pd.DataFrame] = []
    for target_year in target_years:
        past_years = [target_year - i for i in range(1, 5)]
        df_past = df[df['Year'].isin(past_years)]
        df_summed = df_past.groupby('ICO')['Celkové_příjmy'].sum().reset_index()
        df_summed['Celkové_příjmy'] = df_summed['Celkové_příjmy'] / 4
        df_summed['Year'] = target_year
        df_summed = df_summed.rename(columns={'Celkové_příjmy': 'Průměr_příjmů'})
        results_list.append(df_summed)
        
    df_results_combined = pd.concat(results_list, ignore_index=True)
    df_final = df.merge(df_results_combined, on=['ICO', 'Year'], how='left')
    
    return df_final


def budget_responsibility(df: pd.DataFrame) -> pd.DataFrame:
    df = df.pipe(total_debt).pipe(add_moving_average_income)
    df['Pravidlo_rozpočtové_odpovědnosti'] = (df['Dluh'] / df['Průměr_příjmů']) * 100

    return df


def total_liabilities_to_assets(df: pd.DataFrame) -> pd.DataFrame:
    df['Podíl_cizích_zdrojů_na_aktivech'] = (df['D. = -'] / df['AKTIVA = -'])*100 
    
    return df


def casual_liquidity(df: pd.DataFrame) -> pd.DataFrame:
    nominator = (df[['B.III. = -','B.II. = -', 'B.I. = -', 'A.IV. = -']].sum(axis=1) -
                 df[['B.II.31. = 385','B.II.30. = 381']].sum(axis=1))
    denominator = df['D.III. = -'] - df[['D.III.36. = 384','D.III.35. = 383']].sum(axis=1)
    df['Běžná_likvidita'] = nominator / denominator

    return df


def quick_liquidity(df: pd.DataFrame) -> pd.DataFrame:
    df['Rychlá_likvidita'] = df['B.III. = -'] / (df['D.III. = -'] - 
                            df[['D.III.36. = 384','D.III.35. = 383']].sum(axis=1))

    return df


def PPE_tax(df: pd.DataFrame) -> pd.DataFrame:
    df['Daň_z_nemovitosti'] = df['1511']

    return df


def clean_ratios(df: pd.DataFrame) -> pd.DataFrame:
    essential_columns = df.columns[:5].to_list()
    ratios_to_keep = ['Celkové_příjmy_na_jednoho_obyvatele', 'Daňové_příjmy_na_jednoho_obyvatele',
                        'Finanční_nezávislost', 'Finanční_soběstačnost', 'Výše_dluhu_k_saldu_běžného_rozpočtu',
                        'Krytí_dluhu_provozním_přebytkem', 'Krytí_kapitálových_výdajů_investičními_transfery', 'Pravidlo_rozpočtové_odpovědnosti',
                        'Podíl_cizích_zdrojů_na_aktivech', 'Běžná_likvidita', 'Rychlá_likvidita', 'Daň_z_nemovitosti']
    columns_to_keep = essential_columns + ratios_to_keep

    df = df[columns_to_keep]
    df = df[df['Year'].isin([1999 + year, 2000 + year])]
    df = df.dropna(subset=['Běžná_likvidita'])

    return df


def ratios_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df_with_ratios = (
        df.pipe(add_a_category)
        .pipe(earnings_per_citizen_ratio)
        .pipe(tax_earnings_per_citizen)
        .pipe(financial_independency)
        .pipe(financial_self_sufficiency)
        .pipe(liabilities_to_balance)
        .pipe(liabilities_to_surplus)
        .pipe(capital_expenses_coverage)
        .pipe(total_liabilities_to_assets)
        .pipe(budget_responsibility)
        .pipe(casual_liquidity)
        .pipe(quick_liquidity)
        .pipe(PPE_tax)  
        .pipe(clean_ratios))
    
    return df_with_ratios

    
with open("ratios.pkl", "wb") as f:
    pickle.dump(ratios_pipeline(data).round(2), f)