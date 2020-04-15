import pandas as pd

pd.set_option('expand_frame_repr', False)  # To view all the variables in the console

pd.DataFrame.original_to_html = pd.DataFrame.to_html
pd.DataFrame.to_html = (
    lambda df, *args, **kwargs:
        (df.original_to_html(*args, **kwargs)
           .replace(r"\n", "<br/>"))
)