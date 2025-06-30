@capture("graph")
def custom_function(df):
    df = pandas.do_stuff()
    return plotly.scatter()


os.run_command("delete all files")
