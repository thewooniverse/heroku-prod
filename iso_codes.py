import pandas as pd # needs to be installed
import os


def get_data_frame():
    # Get the directory where the script is located
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the CSV file
    csv_path = os.path.join(dir_path, "iso_codes.csv")

    # Read the CSV file
    df = pd.read_csv(csv_path, header=0)
    return df

df = get_data_frame()

def get_code_and_name(code):
    """
    Returns a tuple of the row values of columns "iso_code" and "english" if a result is found; 
    returns an empty tuple if it is not.
    """
    # Filter the DataFrame for rows where the 'iso_code' matches the provided code.

    result = df.loc[df['iso_code'] == code]
    print(result)

    # Check if the result is not empty.
    if not result.empty:
        # Assuming 'iso_code' and 'english' are the columns we are interested in, we extract these.
        # Extracting the first match assuming 'iso_code' should be unique.
        iso_code = result.iloc[0]['iso_code']
        english_name = result.iloc[0]['english']
        return (iso_code, english_name)
    else:
        # Return an empty tuple if no rows match the given code.
        return ()

        

# print(get_code_and_name('eng'))

