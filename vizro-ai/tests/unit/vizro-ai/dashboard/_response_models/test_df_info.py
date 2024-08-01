from vizro_ai.dashboard._response_models.df_info import _get_df_info


def test_get_df_info(df, df_schema):
    actual_df_schema, _ = _get_df_info(df=df)

    assert actual_df_schema == df_schema
