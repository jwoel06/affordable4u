import pandas as pd
import sqlite3

def import_to_csvs():
    conn = sqlite3.connect('new_college.db')

    df1 = pd.read_csv('data/social_impact_final.csv')
    df1.to_sql('social', conn, if_exists='replace', index=False)
    
    conn.close()
    print('To db is done')

if __name__ == "__main__":
    import_to_csvs()