#from data_cleaning_script import years_to_analyze
import pandas as pd
import pickle
import numpy as np
from typing import Callable

with open("ratios.pkl", "rb") as f:
    ratios: pd.DataFrame = pickle.load(f)

list_of_categories = ratios['Category'].unique()
ratio_weights = np.array([0.05,0,0.05,0.15,0.2,0.15,0.05,0.15,0.05,0.1,0.05,0])
IQR_parameter = 1.5
years_to_analyse = sorted(ratios['Year'].unique())[-2:]
list_of_ratios = ratios.columns[5:]


def fixed_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    df["Výše_dluhu_k_saldu_běžného_rozpočtu"] = pd.Series([float("-inf"),0.75,1.5,2.25,3,3.75,4.5,5.25,6,6.75,7,float("inf")])
    df["Krytí_dluhu_provozním_přebytkem"] = pd.Series([float("-inf"),0.75,1.5,2.25,3,3.75,4.5,5.25,6,6.75,7,float("inf")])
    df['Pravidlo_rozpočtové_odpovědnosti'] = pd.Series([0,1.4,6.8,12.2,17.6,23,28.4,33.8,39.2,44.6,50,float('inf')])
    df['Podíl_cizích_zdrojů_na_aktivech'] = pd.Series([0,5,7,9,11,13,16,18,20,22,23,float('inf')])
    df['Běžná_likvidita'] = pd.Series([0,1.4,1.8,2.2,2.6,3.0,3.4,3.8,4.2,4.8,5.0,float('inf')])
    df['Rychlá_likvidita'] = pd.Series([0,1.3,1.6,1.9,2.2,2.5,2.8,3.1,3.4,3.7,4.0,float('inf')])

    return df


def complete_all_years(func: Callable[[int, str], pd.DataFrame]) -> pd.DataFrame:
    list_to_concat: list[pd.DataFrame] = []

    for category in list_of_categories:
        list_of_years: list[pd.DataFrame] = [func(i, category) for i in years_to_analyse]
        years_df = pd.concat(list_of_years, axis=0, ignore_index=True)
        
        if 'Category' not in years_df.columns:
            years_df.insert(0,'Category', category)
        
        list_to_concat.append(years_df)
    complete_df = pd.concat(list_to_concat, axis=0, ignore_index=True)

    return complete_df


def category_percentiles(year: int, category: str) -> pd.DataFrame:
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

with open("percentiles.pkl", "wb") as f:
    pickle.dump(complete_all_years(category_percentiles).round(1), f)


def assign_points(year: int, category: str) -> pd.DataFrame:
    reversed_percentiles = ['Výše_dluhu_k_saldu_běžného_rozpočtu', 'Krytí_dluhu_provozním_přebytkem',
                            'Pravidlo_rozpočtové_odpovědnosti', 'Podíl_cizích_zdrojů_na_aktivech']
    list_of_points: list[pd.Series] = []
  
    df_year = ratios[ratios['Year'] == year]
    df_year = df_year[df_year['Category'] == category]
    percentiles_df = complete_all_years(category_percentiles)
    percentiles_df = percentiles_df[percentiles_df['Category'] == category]
    percentiles_df_year = percentiles_df[percentiles_df['Year'] == year]

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


def final_score(df: pd.DataFrame) -> pd.DataFrame:
    scoring_columns = df.columns[-12:]
    df['Finální_skóre'] = df[scoring_columns].dot(ratio_weights).round(1)

    return df


def points_pipeline(year: int, category: str) -> pd.DataFrame:
    df = assign_points(year, category)
    df = final_score(df)

    return df


with open("points.pkl", "wb") as f:
    pickle.dump(complete_all_years(points_pipeline).round(2), f)

