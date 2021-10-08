import pandas as pd
from core_func import sec_to_hhmm


def add_hovertext_difference(df):
    df = pd.DataFrame.from_dict(df)
    df.loc['drive_minus_train'] = df.loc['train_time'] - df.loc['drive_time']
    df.loc['hovertext_train'] = f"{df.loc['destination']}<br>{df.loc['train_time'].apply(sec_to_hhmm)}"
    df.loc['hovertext_drive'] = f"{df.loc['destination']}<br>{df.loc['drive_time'].apply(sec_to_hhmm)}"
    df.loc['hovertext_diff'] = f"{df.loc['destination']}<br>{df.loc['drive_minus_train'].apply(sec_to_hhmm)}"

    return df.to_dict()
