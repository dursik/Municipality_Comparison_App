import argparse
import pickle
from functools import partial
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

ratio_weights = {
    'Celkové_příjmy_na_jednoho_obyvatele': 0.05,
    'Daňové_příjmy_na_jednoho_obyvatele': 0,
    'Finanční_nezávislost': 0.05,
    'Finanční_soběstačnost': 0.15,
    'Výše_dluhu_k_saldu_běžného_rozpočtu': 0.2,
    'Krytí_dluhu_provozním_přebytkem': 0.15,
    'Krytí_kapitálových_výdajů_investičními_transfery': 0.05,
    'Pravidlo_rozpočtové_odpovědnosti': 0.15,
    'Podíl_cizích_zdrojů_na_aktivech': 0.05,
    'Běžná_likvidita': 0.1,
    'Rychlá_likvidita': 0.05,
    'Daň_z_nemovitosti_na_jednoho_obyvatele': 0}
IQR_parameter = 1.5


def fixed_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    df["Výše_dluhu_k_saldu_běžného_rozpočtu"] = pd.Series([float("-inf"),0.75,1.5,2.25,3,3.75,4.5,5.25,6,6.75,7,float("inf")])
    df["Krytí_dluhu_provozním_přebytkem"] = pd.Series([float("-inf"),0.75,1.5,2.25,3,3.75,4.5,5.25,6,6.75,7,float("inf")])
    df['Pravidlo_rozpočtové_odpovědnosti'] = pd.Series([0,1.4,6.8,12.2,17.6,23,28.4,33.8,39.2,44.6,50,float('inf')])
    df['Podíl_cizích_zdrojů_na_aktivech'] = pd.Series([0,5,7,9,11,13,16,18,20,22,23,float('inf')])
    df['Běžná_likvidita'] = pd.Series([0,1.4,1.8,2.2,2.6,3.0,3.4,3.8,4.2,4.8,5.0,float('inf')])
    df['Rychlá_likvidita'] = pd.Series([0,1.3,1.6,1.9,2.2,2.5,2.8,3.1,3.4,3.7,4.0,float('inf')])

    return df


def complete_all_years(func: Callable[[int, str], pd.DataFrame],
                       categories: list[str],
                       years: list[int]) -> pd.DataFrame:
    list_to_concat: list[pd.DataFrame] = []

    for category in categories:
        list_of_years: list[pd.DataFrame] = [func(i, category) for i in years]
        years_df = pd.concat(list_of_years, axis=0, ignore_index=True)

        if 'Category' not in years_df.columns:
            years_df.insert(0,'Category', category)

        list_to_concat.append(years_df)
    complete_df = pd.concat(list_to_concat, axis=0, ignore_index=True)

    return complete_df


def category_percentiles(year: int, category: str,
                         ratios: pd.DataFrame,
                         list_of_ratios: list[str]) -> pd.DataFrame:
    all_percentiles = pd.DataFrame()
    percentile_levels = list(range(10,110,10))

    year_ratios = ratios[ratios['Year'] == year]
    year_ratios = year_ratios[year_ratios['Category'] == category]

    if year_ratios.empty:
        for i in list_of_ratios:
             single_percentiles = pd.Series([float('-inf')] + [np.nan]*10 + [float('inf')], name=f'{i}')
             all_percentiles = pd.concat([all_percentiles, single_percentiles], axis=1)
        all_percentiles.insert(0, 'Year', year)
        return fixed_percentiles(all_percentiles)

    for i in list_of_ratios:
        data: pd.Series = year_ratios.loc[:, i].dropna()
        data = pd.to_numeric(data, errors='coerce').dropna()

        if data.empty:
            single_percentiles = [float('-inf')] + [np.nan]*10 + [float('inf')]
        else:
            Q1, Q3 = data.quantile([0.25,0.75]).values
            IQR = Q3 - Q1

            filtered_data: pd.Series = data[(data >= (Q1 - IQR_parameter*IQR))
                                          & (data <= (Q3 + IQR_parameter*IQR))]

            if filtered_data.empty:
                calculated_percentiles = [np.nan]*10
            else:
                calculated_percentiles = np.percentile(filtered_data, percentile_levels).tolist()

            single_percentiles = [float('-inf')] + calculated_percentiles + [float('inf')]

        single_percentiles = pd.Series(single_percentiles, name=f'{i}')
        all_percentiles = pd.concat([all_percentiles, single_percentiles], axis=1)

    all_percentiles.insert(0, 'Year', year)
    all_percentiles = fixed_percentiles(all_percentiles)

    return all_percentiles


def assign_points(year: int, category: str,
                  ratios: pd.DataFrame,
                  list_of_ratios: list[str],
                  percentiles_df: pd.DataFrame) -> pd.DataFrame:
    reversed_percentiles = ['Výše_dluhu_k_saldu_běžného_rozpočtu', 'Krytí_dluhu_provozním_přebytkem',
                            'Pravidlo_rozpočtové_odpovědnosti', 'Podíl_cizích_zdrojů_na_aktivech']
    list_of_points: list[pd.Series] = []

    df_year = ratios[ratios['Year'] == year]
    df_year = df_year[df_year['Category'] == category]
    percentiles_category = percentiles_df[percentiles_df['Category'] == category]
    percentiles_df_year = percentiles_category[percentiles_category['Year'] == year]

    for i in list_of_ratios:
        basket = list(percentiles_df_year[str(i)].values)
        data: pd.Series = df_year.loc[:,str(i)]

        if i in reversed_percentiles:
            number_of_bins = len(set(basket))-2
            names = list(range(number_of_bins,-1,-1))
            single_points: pd.Series = pd.Series(
                pd.cut(data, basket, include_lowest=True, duplicates='drop', labels=names),
                name=str(i) + '_score').astype(float)

        else:
            number_of_bins = len(set(basket))-1
            names = list(range(0,number_of_bins))
            single_points: pd.Series = pd.Series(
                pd.cut(data, basket, include_lowest=True, duplicates='drop', labels=names),
                name=str(i) + '_score').astype(float)
        list_of_points.append(single_points)

    df_year = pd.concat([df_year] + list_of_points, axis=1)

    return df_year


def check_ratio_weights(list_of_ratios: list[str]) -> None:
    missing = [ratio for ratio in list_of_ratios if ratio not in ratio_weights]
    unknown = [ratio for ratio in ratio_weights if ratio not in list(list_of_ratios)]
    total = round(sum(ratio_weights.values()), 6)

    if missing:
        raise SystemExit(f'V ratio_weights chybí váha pro: {", ".join(missing)}')
    if unknown:
        raise SystemExit(f'ratio_weights zná ukazatele, které nejsou v datech: {", ".join(unknown)}')
    if total != 1:
        raise SystemExit(f'Součet vah v ratio_weights musí být 1, je {total}')


def final_score(df: pd.DataFrame) -> pd.DataFrame:
    scoring_columns = [f'{ratio}_score' for ratio in ratio_weights]
    weights = np.array(list(ratio_weights.values()))
    df['Finální_skóre'] = df[scoring_columns].dot(weights).round(1)

    return df


def points_pipeline(year: int, category: str,
                    ratios: pd.DataFrame,
                    list_of_ratios: list[str],
                    percentiles_df: pd.DataFrame) -> pd.DataFrame:
    df = assign_points(year, category, ratios, list_of_ratios, percentiles_df)
    df = final_score(df)

    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Spočítá percentilové hranice a bodové skóre obcí z ratios.pkl.')
    parser.add_argument('--ratios', type=Path, default=Path('ratios.pkl'),
                        help='vstupní pickle z ratios_script.py (výchozí: ratios.pkl)')
    parser.add_argument('--percentiles-output', type=Path, default=Path('percentiles.pkl'),
                        help='výstupní pickle s hranicemi (výchozí: percentiles.pkl)')
    parser.add_argument('--points-output', type=Path, default=Path('points.pkl'),
                        help='výstupní pickle se skóre (výchozí: points.pkl)')

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.ratios.is_file():
        raise SystemExit(f'Soubor {args.ratios} neexistuje')

    with open(args.ratios, 'rb') as f:
        ratios: pd.DataFrame = pickle.load(f)

    list_of_categories = list(ratios['Category'].unique())
    years_to_analyse = sorted(ratios['Year'].unique())[-2:]
    list_of_ratios = ratios.columns[6:]
    check_ratio_weights(list_of_ratios)

    print(f'Zpracovávám roky {years_to_analyse}, kategorií: {len(list_of_categories)}')

    percentiles_df = complete_all_years(
        partial(category_percentiles, ratios=ratios, list_of_ratios=list_of_ratios),
        list_of_categories, years_to_analyse)

    with open(args.percentiles_output, 'wb') as f:
        pickle.dump(percentiles_df.round(1), f)

    print(f'Uloženo {len(percentiles_df)} řádků do {args.percentiles_output}')

    points_df = complete_all_years(
        partial(points_pipeline, ratios=ratios, list_of_ratios=list_of_ratios,
                percentiles_df=percentiles_df),
        list_of_categories, years_to_analyse)

    with open(args.points_output, 'wb') as f:
        pickle.dump(points_df.round(2), f)

    print(f'Uloženo {len(points_df)} řádků do {args.points_output}')


if __name__ == '__main__':
    main()
