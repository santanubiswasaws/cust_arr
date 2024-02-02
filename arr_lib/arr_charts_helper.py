import pandas as pd

def prepare_waterfall_data(input_df):

    df = input_df.copy()

    df['nb_end'] = df['preRev'] + df['newBusiness']

    # Add the 'ex_end' column as the sum of 'nb_end' and 'upSell'
    df['ex_end'] = df['nb_end'] + df['upSell']

    # Add the 'cnt_end' column as the sum of 'ex_end' and 'downSell'
    df['cnt_end'] = df['ex_end'] + df['downSell']

    # Add the 'churn_end' column as the sum of 'cnt_end' and 'churn'
    df['churn_end'] = df['cnt_end'] + df['churn']

    # Adding End Period 
    closing_period_data = df.iloc[-1]
    # Sample row data for 'End Period'
    end_period_row = pd.DataFrame({
        'period': ['End Period'],
        'preRev': [closing_period_data['curRev']],
        'curRev': [closing_period_data['curRev']]
        # 'churn_offset': [closing_period_data['churn_offset']]
        # Include other necessary columns here
    })
    # Append the 'End Period' 
    df = pd.concat([df, end_period_row], ignore_index=True)


    df['lead_period'] = df['period'].shift(-1).ffill()


    df['curMid'] = df['curRev'] / 2
    df['preMid'] = df['preRev'] / 2


    # Create boolean masks for non-zero values in each category
    has_newBusiness = df['newBusiness'] != 0
    has_upSell = df['upSell'] != 0
    has_downSell = df['downSell'] != 0
    has_churn = df['churn'] != 0

    # Convert boolean masks to integers (0 or 1)
    newBusiness_int = has_newBusiness.astype(int)
    upSell_int = has_upSell.astype(int)
    downSell_int = has_downSell.astype(int)
    churn_int = has_churn.astype(int)

    # Calculate cumulative offsets for each category
    # Each offset is based on the presence of the previous categories
    df['nb_offset'] = 10 * newBusiness_int
    df['ex_offset'] = df['nb_offset'] + 10 * upSell_int
    df['cnt_offset'] = df['ex_offset'] + 10 * downSell_int
    df['churn_offset'] = df['cnt_offset'] + 10 * churn_int

    return df
