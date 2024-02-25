from options_terminal import Options_Chain
from flask import Flask, render_template, request
import psycopg2

class Options_Application:
    def __init__(self, ticker, expiration_date = None):
        self.ticker = ticker
        self.exp_date = expiration_date


    def lookup_expiration_dates(self):
        options_chain = Options_Chain(self.ticker) 
        return options_chain.lookup_expiration_dates()
    

    def input_options_to_dataset(self, buying_method):
        if buying_method == 'call':
            options_chain = Options_Chain(self.ticker, self.exp_date)
            options_chain.truncate_database('call')
            options_chain.front_month_call_options()
        
        elif buying_method == 'put':
            options_chain = Options_Chain(self.ticker, self.exp_date)
            options_chain.truncate_database('put')
            options_chain.front_month_put_options()

        elif buying_method == 'all':
            options_chain = Options_Chain(self.ticker, self.exp_date)
            options_chain.remove_index() # Removing an index makes inserting values quicker
            options_chain.truncate_database('all')
            options_chain.front_month_call_options()
            options_chain.front_month_put_options()
            options_chain.add_index() # An index is only necessary for this buying method because we JOIN the strike prices together, and an index expedites this task


    # Pull out the data from the options_research database
    def extract_options_from_dataset(self, buying_method):
        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        if buying_method == 'call':
            cur.execute('SELECT * FROM call_options_chain')

            rows = cur.fetchall()

            columns = ('id', 'symbol', 'contract_name', 'bid', 'ask', 'mid', 'premium', 'change', 'volume', 
                       'open_interest', 'implied_volatility', 'expiry_date', 'strike', 'added_time')

            options_table = self.dictionize_and_zip(columns, rows)

            conn.commit()
            cur.close()
            conn.close()
        

        elif buying_method == 'put':
            cur.execute('SELECT * FROM put_options_chain')

            rows = cur.fetchall()

            columns = ('id', 'symbol', 'contract_name', 'bid', 'ask', 'mid', 'premium', 'change', 'volume', 
                       'open_interest', 'implied_volatility', 'expiry_date', 'strike', 'added_time')

            options_table = self.dictionize_and_zip(columns, rows)

            conn.commit()
            cur.close()
            conn.close()
        

        elif buying_method == 'all':
            cur.execute("""
                CREATE TABLE call_and_put_options_chain AS
                SELECT 
                    coc.id AS id_call,
                    coc.symbol AS symbol_call,
                    coc.contract_name AS contract_name_call, 
                    coc.bid AS bid_call,
                    coc.ask AS ask_call,
                    coc.mid AS mid_call,
                    coc.premium AS premium_call,
                    coc.change AS change_call,
                    coc.volume AS volume_call,
                    coc.open_interest AS open_interest_call,
                    coc.implied_volatility AS implied_volatility_call,
                    coc.expiry_date AS expiry_date_call,
                    coc.strike AS strike_call,
                    coc.added_time AS added_time_call,

                    poc.id AS id_put,
                    poc.symbol AS symbol_put,
                    poc.contract_name AS contract_name_put,
                    poc.bid AS bid_put,
                    poc.ask AS ask_put,
                    poc.mid AS mid_put,
                    poc.premium AS premium_put,
                    poc.change AS change_put,
                    poc.volume AS volume_put,
                    poc.open_interest AS open_interest_put,
                    poc.implied_volatility AS implied_volatility_put,
                    poc.expiry_date AS expiry_date_put,
                    poc.strike AS strike_put,
                    poc.added_time AS added_time_put

                FROM call_options_chain coc
                JOIN put_options_chain poc ON coc.strike = poc.strike;

                SELECT * 
                FROM call_and_put_options_chain;
                """)

            rows = cur.fetchall()

            columns = ('id_call', 'symbol_call', 'contract_name_call', 'bid_call', 'ask_call', 'mid_call', 'premium_call', 'change_call', 'volume_call', 
                       'open_interest_call', 'implied_volatility_call', 'expiry_date_call', 'strike_call', 'added_time_call', 
                        'id_put', 'symbol_put', 'contract_name_put', 'bid_put', 'ask_put', 'mid_put',  'premium_put', 'change_put', 'volume_put',
                        'open_interest_put', 'implied_volatility_put', 'expiry_date_put', 'strike_put', 'added_time_put')

            options_table = self.dictionize_and_zip(columns, rows)

            conn.commit()
            cur.close()
            conn.close()

        return options_table
    

    # If 'all' is selected as the buying_method, call both 'call' and 'put
    def extract_greeks_from_dataset(self, buying_method):
        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        if buying_method == 'call':
            cur.execute('SELECT * FROM call_options_greeks;') #fix this tmrw

            rows = cur.fetchall()

            columns = ('id', 'call_options_chain_id', 'contract_name', 'delta', 'gamma', 'theta', 'vega', 'rho', 'day_high', 'day_low',  'previous_close',
                        'open', 'tick', 'bid_size', 'ask_size', 'contract_high', 'contract_low', 'market', 'days_until_expiration',
                        'volume', 'open_interest', 'implied_volatility')
            
            greeks_table = self.dictionize_and_zip(columns, rows)

            conn.commit()
            cur.close()
            conn.close()


        elif buying_method == 'put':
            cur.execute('SELECT * FROM put_options_greeks;')

            rows = cur.fetchall()

            columns = ('id', 'put_options_chain_id', 'contract_name', 'delta', 'gamma', 'theta', 'vega', 'rho', 'day_high', 'day_low',  'previous_close',
                        'open', 'tick', 'bid_size', 'ask_size', 'contract_high', 'contract_low', 'market', 'days_until_expiration',
                        'volume', 'open_interest', 'implied_volatility')
            
            greeks_table = self.dictionize_and_zip(columns, rows)

            conn.commit()
            cur.close()
            conn.close()
        
        return greeks_table


    # Helper function to minimize code repetition for combining the columns and the rows to create a dictionary
    def dictionize_and_zip(self, columns, rows):
        table = []

        for row in rows:
                column_row = dict(zip(columns, row))
                table.append(column_row)
        
        return table


# Connect Python w/ HTML via Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/options_form', methods=['GET', 'POST'])
def fetch_input_ticker():
    user_input_ticker_main = None
    user_input_month = None
    user_input_day = None 
    user_input_year = None

    if request.method == 'POST' and 'search_call' in request.form:
        user_input_ticker_main = request.form['user_input_ticker_main'].upper()
        user_input_month = request.form['user_input_month'].title()
        user_input_day = request.form['user_input_day']
        user_input_year = request.form['user_input_year']

        # If the user doesn't specify a date or some parts of the date is missing, we'll assume that they want the entire options dataset for the front month
        if user_input_month == None or user_input_day == None or user_input_year == None:
            expiration_date = None
        else:
            expiration_date = f'{user_input_month} {user_input_day}, {user_input_year}'

        options_application = Options_Application(user_input_ticker_main, expiration_date)
        options_application.input_options_to_dataset('call')
        
        return render_template('index.html',
                               notice=f'Researching {user_input_ticker_main}, at {user_input_month} {user_input_day}, {user_input_year} for calls:',

                               option_chain_title_call=f'{user_input_ticker_main} Option Chain',
                               call_table=options_application.extract_options_from_dataset('call'),

                               option_greeks_title_call=f'{user_input_ticker_main} Option Greeks',
                               call_greeks_table=options_application.extract_greeks_from_dataset('call'))
    

    elif request.method == 'POST' and 'search_put' in request.form:
        user_input_ticker_main = request.form['user_input_ticker_main'].upper()
        user_input_month = request.form['user_input_month'].title()
        user_input_day = request.form['user_input_day']
        user_input_year = request.form['user_input_year']

        # If the user doesn't specify a date or some parts of the date is missing, we'll assume that they want the entire options dataset for the front month
        if user_input_month == None or user_input_day == None or user_input_year == None:
            expiration_date = None
        else:
            expiration_date = f'{user_input_month} {user_input_day}, {user_input_year}'

        options_application = Options_Application(user_input_ticker_main, expiration_date)
        options_application.input_options_to_dataset('put')
        
        return render_template('index.html',
                               notice=f'Researching {user_input_ticker_main}, at {user_input_month} {user_input_day}, {user_input_year} for puts:',

                               option_chain_title_put=f'{user_input_ticker_main} Option Chain',
                               put_table=options_application.extract_options_from_dataset('put'),

                               option_greeks_title_put=f'{user_input_ticker_main} Option Greeks',
                               put_greeks_table=options_application.extract_greeks_from_dataset('put'))
    

    elif request.method == 'POST' and 'search_all' in request.form:
        user_input_ticker_main = request.form['user_input_ticker_main'].upper()
        user_input_month = request.form['user_input_month'].title()
        user_input_day = request.form['user_input_day']
        user_input_year = request.form['user_input_year']

        # If the user doesn't specify a date or some parts of the date is missing, we'll assume that they want the entire options dataset for the front month
        if user_input_month == None or user_input_day == None or user_input_year == None:
            expiration_date = None
        else:
            expiration_date = f'{user_input_month} {user_input_day}, {user_input_year}'

        options_application = Options_Application(user_input_ticker_main, expiration_date)
        options_application.input_options_to_dataset('all') 
        
        return render_template('index.html',
                               notice=f'Researching {user_input_ticker_main}, at {user_input_month} {user_input_day}, {user_input_year} for calls and puts:',
                               option_chain_title_all=f'{user_input_ticker_main} Option Chain',

                               call_and_put_table=options_application.extract_options_from_dataset('all'),
 
                               call_table=options_application.extract_options_from_dataset('call'),
                               put_talbe=options_application.extract_options_from_dataset('put'),

                               option_greeks_title_call=f'{user_input_ticker_main} Option Greeks',
                               option_greeks_title_put=f'{user_input_ticker_main} Option Greeks',

                               call_greeks_table=options_application.extract_greeks_from_dataset('call'), # Call both 'call' and 'put' 
                               put_greeks_table=options_application.extract_greeks_from_dataset('put')) # since we are looking at all of the buying methods
    

    elif request.method == 'POST' and 'search_expiry_dates' in request.form:
        user_input_ticker = request.form['user_input_ticker'].upper()

        fetch_options_application_ticker = Options_Application(user_input_ticker)
        fetch_exp_dates = fetch_options_application_ticker.lookup_expiration_dates()

        if len(fetch_exp_dates) == 0:
            no_exp_date_list = 'This stock/ETF does not exist'
            exp_date_list = ''
            ticker_notice = ''
        else:
            exp_date_list = fetch_exp_dates
            no_exp_date_list = ''
            ticker_notice = f'Expiration dates for: {user_input_ticker}'

        return render_template('index.html',
                               exp_date_list=exp_date_list,
                               no_exp_date_list=no_exp_date_list,
                               ticker_notice=ticker_notice)


if (__name__ == '__main__'):
    app.run(debug=True)

