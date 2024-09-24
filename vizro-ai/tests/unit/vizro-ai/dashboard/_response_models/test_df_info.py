from pandas.testing import assert_frame_equal

from vizro_ai.dashboard._response_models.df_info import _get_df_info


def test_get_df_info(df, df_schema, df_sample):
    actual_df_schema, actual_df_sample = _get_df_info(df=df)

    assert actual_df_schema == df_schema
    assert_frame_equal(actual_df_sample, df_sample)
