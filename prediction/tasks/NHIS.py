"""Build prediction tasks for the NHIS database."""

import pandas as pd

from database import TB
from prediction import PredictionTask


df_with_MV = TB.encoded_dataframes['20000']
df_mv = TB.encoded_missing_values['20000']
df_imputed = pd.read_csv('imputed/TB_20000_imputed_rounded_Iterative.csv',
                         sep=';', index_col=0).astype(df_with_MV.dtypes)


# Task 1: Death prediction
to_predict_1 = "Décès"
to_drop_1 = [
    "Date de décès (à l'hôpital après sortie de réanimation)",
    "Cause du décès_A survécu",
    "Cause du décès_Autre (précisez ci-dessous)",
    "Cause du décès_Choc hémorragique",
    "Cause du décès_Choc septique",
    "Cause du décès_Défaillance multi-viscérale",
    "Cause du décès_LATA",
    "Cause du décès_Mort encéphalique",
    "Cause du décès_Trauma cranien",
    "Cause du décès_z MISSING_VALUE",
    "Transfert secondaire, pourquoi ?_Pas de transfert",
    "Transfert secondaire, pourquoi ?_Plateau technique insuffisant",
    "Transfert secondaire, pourquoi ?_Rapprochement familial",
    "Transfert secondaire, pourquoi ?_z MISSING_VALUE",
    "Sortie_Autre réanimation",
    "Sortie_Centre de rééducation",
    "Sortie_Domicile",
    "Sortie_Service hospitalier",
    "Sortie_z MISSING_VALUE",
    "Glasgow de sortie",
    "Nombre de jours à l'hôpital",
    "Durée de séjour en réa- si date de sortie connue, durée de séjour = (date sortie - date d entrée)- si date de sortie inconnue, d",
    "Nombre de jours de VM",
    "Procédure limitations de soins (LATA)",
]

death_imputed = PredictionTask(
    df=df_imputed,
    to_predict=to_predict_1,
    to_drop=to_drop_1
)

death_with_MV = PredictionTask(
    df=df_with_MV,
    to_predict=to_predict_1,
    to_drop=to_drop_1
)

# Task 2: Platelet prediciton (https://arxiv.org/abs/1909.06631)
def transform_df_2(df):
    """Build df with appropiate features for platelet prediciton following
    github.com/wjiang94/ABSLOPE/blob/master/ABSLOPE/OnlineSupp/OnlineSupp.pdf"""
    df = df.copy()
    df['Age'] = df['Age du patient (ans)']
    df['SI'] = df['FC en phase hospitalière'].divide(df['Pression Artérielle Systolique - PAS'])
    df['MBP'] = (2*df['Pression Artérielle Diastolique - PAD']+df['Pression Artérielle Systolique - PAS'])/3
    df['Delta.hemo'] = df['Delta Hémocue']
    df['Time.amb'] = df['Délai « arrivée sur les lieux - arrivée hôpital »']
    df['Lactate'] = df['Lactates']
    df['Temp'] = df['Température']
    df['HR'] = df['FC en phase hospitalière']
    df['VE'] = df['Cristalloïdes']+df['Colloïdes']
    df['RBC'] = df['Choc hémorragique (? 4 CGR sur 6h)']
    df['SI.amb'] = df['Fréquence cardiaque (FC) à l arrivée du SMUR'].divide(df['Pression Artérielle Systolique (PAS) à l arrivée du SMUR'])
    df['MAP.amb'] = (2*df['Pression Artérielle Diastolique (PAD) à l arrivée du SMUR']+df['Pression Artérielle Systolique (PAS) à l arrivée du SMUR'])/3
    df['HR.max'] = df['Fréquence cardiaque (FC) maximum']
    df['SBP.min'] = df['Pression Artérielle Systolique (PAS) minimum']
    df['DBP.min'] = df['Pression Artérielle Diastolique (PAD) minimum']

    # Drop rows with missing values in the feature to predict
    df.dropna(axis=0, subset=['Plaquettes'], inplace=True)

    return df


to_predict_2 = 'Plaquettes'
to_keep_2 = [
    'Age',
    'SI',
    'MBP',
    'Delta.hemo',
    'Time.amb',
    'Lactate',
    'Temp',
    'HR',
    'VE',
    'RBC',
    'SI.amb',
    'MAP.amb',
    'HR.max',
    'SBP.min',
    'DBP.min'
]

platelet_imputed = PredictionTask(
    df=transform_df_2(df_imputed),
    to_predict=to_predict_2,
    to_keep=to_keep_2
)

platelet_with_MV = PredictionTask(
    df=transform_df_2(df_with_MV),
    to_predict=to_predict_2,
    to_keep=to_keep_2
)

# All tasks
tasks = {
    'death_imputed': death_imputed,
    'death_with_MV': death_with_MV,
    'platelet_imputed': platelet_imputed,
    'platelet_with_MV': platelet_with_MV,
}
