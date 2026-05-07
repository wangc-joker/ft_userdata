def populate_exit_trend(strategy, df, metadata: dict):
    df.loc[:, "exit_long"] = 0
    df.loc[:, "exit_short"] = 0

    return df
