import pandas as pd
import psycopg2 as pg
from sshtunnel import SSHTunnelForwarder
from datetime import date, timedelta
import os 
from helper_functions import  create_postgres_engine


# Define a function to read table names from the information schema
def get_table_names(engine, schema=None, regex_condition=None):
    schema_filter = f"AND table_schema = '{schema}'" if schema else ""
    regex_filter = f"AND table_name ~ '{regex_condition}'" if regex_condition else ""

    information_schema_table_names_query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE 1=1
        {schema_filter}
        {regex_filter}
    """
    
    table_names = pd.read_sql(information_schema_table_names_query, engine)
    return table_names

# Extract data from PostgreSQL for a specific table
def extract_data(table_name, engine):
    query = f'SELECT * FROM core.{table_name}'
    with engine.connect() as connection:
        result = connection.execute(query)
        records = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(records, columns=columns)
    return df

# Perform data profiling for a specific table
def perform_data_profiling(table_name, df, raw_meta_data, today, output_path):
    summary_profile = pd.DataFrame()
    indicators = []
    indicator_values = []

    df_profile = pd.DataFrame()
    col_value_profile = []
    col_nulls = []
    col_unique_values = []

    relevant_raw_meta_data = raw_meta_data[raw_meta_data['table_name'] == table_name]
    df_table_cols = list(df.columns)

    total_rows = df.shape[0]
    total_columns = df.shape[1]
    total_cells = df.size
    total_nulls = sum(list(df.isna().sum()))
    missing_ratio = total_nulls / total_cells
    data_types = dict(relevant_raw_meta_data['data_type'].value_counts(dropna=False))

    for col in df_table_cols:
        col_profile_dict = dict(df[col].value_counts())

        col_nulls.append(df[col].isna().sum())
        col_value_profile.append(col_profile_dict)
        col_unique_values.append(len(df[col].unique()))

    df_profile['Column Name'] = df_table_cols
    df_profile['Value Profiles'] = col_value_profile
    df_profile['Column Nulls'] = col_nulls
    df_profile['Number of Unique Values'] = col_unique_values

    data_profile_complete = pd.merge(df_profile, relevant_raw_meta_data, how='inner', right_on='column_name', left_on='Column Name')

    indicators = [
        "Total Variables",
        "Total Cells",
        "Total Rows",
        "Estimated Size in Memory (Python)",
        "Total Non-empty Values",
        "Total Nulls",
        "Null to Total Ratio",
        "Unique Data Types"
    ]
    indicator_values = [
        total_columns,
        total_cells,
        total_rows,
        "TBD",
        total_cells - total_nulls,
        total_nulls,
        round(missing_ratio, 2),
        data_types
    ]

    summary_profile["Indicator"] = indicators
    summary_profile["Indicator Value"] = indicator_values

    # Construct the output file path
    file_name = f'Profile_{table_name}_{today}.xlsx'
    output_file_path = os.path.join(output_path, file_name)
    # Save the Excel file to the specified output path
    writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')
    data_profile_complete.to_excel(writer, sheet_name='Detailed Profile')
    df_profile.to_excel(writer, sheet_name='Basic Profile')
    summary_profile.to_excel(writer, sheet_name='Summary Profile')
    writer.save()
    writer.close()

# Main function to execute data profiling
def main(output_path):
    today = date.today()

    engine = create_postgres_engine()
    table_names = get_table_names(engine)
    raw_meta_data = pd.read_sql("SELECT * FROM information_schema.columns", engine)  # Adjust the query accordingly

    for table_name in table_names['table_name']:
        print(f"Profiling... {table_name}")
        df = extract_data(table_name, engine)
        perform_data_profiling(table_name, df, raw_meta_data, today, output_path)

if __name__ == "__main__":
    main('./profiles/')
