import pandas as pd
import sqlite3

def import_to_csvs():
    conn = sqlite3.connect('college.db')

    df1 = pd.read_csv('data/AffordabilityGapData.csv')
    df1.to_sql('affordability', conn, if_exists='replace', index=False)
    
    df2 = pd.read_csv('data/CollegeResultsData.csv')
    df2.to_sql('demographics', conn, if_exists='replace', index=False)

    conn.close()
    print('To db is done')

if __name__ == "__main__":
    import_to_csvs()