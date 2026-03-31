def fit_final_model(model, train_df, target_col):
    """
    Fit the chosen model on the full training dataframe.
    """
    if target_col not in train_df.columns:
        raise ValueError(f"Target column '{target_col}' not found in train_df")

    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]

    model.fit(X_train, y_train)
    return model
