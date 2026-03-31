from sklearn.model_selection import train_test_split


def split_train_test(df, test_size=0.2, random_state=42):
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
    )

    return train_df.copy(), test_df.copy()