from yahoo_fin import options
from FOC import FOC
import psycopg2
import psycopg2.extras
from datetime import datetime as dt
import datetime
import calendar


class Options_Chain:
    def __init__(self, ticker, expiration_date = None):
        self.ticker = ticker
        self.exp_date = expiration_date
        # self.symbol_list = full_options_list()
        self.current_month = calendar.month_name[datetime.datetime.now().month] 
        self.current_day = datetime.datetime.now().day
        self.current_year = datetime.datetime.now().year


    # Inject the information into PostgreSQL with their corresponding columns and tables
    def front_month_call_options(self):
        symbol = self.ticker

        # Increment the variable by 1 each time it iterates through a row
        call_options_chain_id = 0

        # If the user specifies an expiry date, only fetch data off of that expiry date
        if self.exp_date != None:
            print(f'Researching {symbol} on {self.exp_date}')

            call_contract = options.get_options_chain(symbol, self.exp_date)['calls']
            self.inject_options_data(call_contract, 'call', call_options_chain_id, symbol, self.exp_date)

            return

        # If not, we use all the front-month expiry dates of the option
        exp_date = options.get_expiration_dates(self.ticker) # Retrieve the expiry dates of the option

        # Loop through each expiry date
        for date in exp_date:
            print(f'Researching {symbol} on {date}')

            # Split the date into 3 pieces: [Month, day, year]
            splitted_date = date.split(' ')

            if int(splitted_date[-1]) == self.current_year and splitted_date[0] == self.current_month:
                date = ' '.join(splitted_date) # Join the dates together once the analysis has passed
                call_contract = options.get_options_chain(symbol, date)['calls'] # Get the options chain of that date

                self.inject_options_data(call_contract, 'call', call_options_chain_id, symbol, date)


    # Extra information for the call options (greeks, bid/ask sizes, etc.)
    # Avoid the last sale, net, bid, ask, timestamp
    def front_month_call_extra(self, i, symbol, date, contract_name, call, strike, call_options_chain_id, volume, oi, impvol):
        print(f'Researching Greeks and additional information of {symbol} at {date} on row {i}')

        # Find the days until the contract expires
        splitted_date = date.split(' ')

        # Also can be used for the expiry day
        day = int(splitted_date[1].replace(',', ''))
        days_until_expiration = day - self.current_day 

        # Get the expiry date format valid for the FOC API
        month_num = str(dt.strptime(splitted_date[0], '%B').month)
        if len(month_num) == 1:
            month_num = f'0{month_num}'

        # Convert to str since the parameters of FOC for the date is string-only
        day_num = str(day)
        if len(day_num) == 1: 
            day_num = f'0{day_num}'

        FOC_expiry_date = f'{splitted_date[-1]}-{month_num}-{day_num}'

        # Initialize the options data
        ref_FOC = FOC()
        contract_symbol = ref_FOC.get_contract_symbol(symbol, FOC_expiry_date, call, strike)
        fetch_contract_symbol_data = ref_FOC.get_options_price_data(contract_symbol)

        # Fetch the extra information for the call contract
        extra_call = fetch_contract_symbol_data.iloc[0] 

        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        insert_postgresql = """
            INSERT INTO call_options_greeks (id, call_options_chain_id, contract_name, delta, gamma, theta, vega, rho, day_high, day_low, prev_close, open, tick, bid_size, ask_size, contract_high, contract_low, market, days_until_expiration, volume, open_interest, implied_volatility)
            VALUES (%(id)s, %(call_options_chain_id)s, %(contract_name)s, %(delta)s, %(gamma)s, %(theta)s, %(vega)s, %(rho)s, %(day_high)s, %(day_low)s, %(prev_close)s, %(open)s, %(tick)s, %(bid_size)s, %(ask_size)s, %(contract_high)s, %(contract_low)s, %(market)s, %(days_until_expiration)s, %(volume)s, %(open_interest)s, %(implied_volatility)s)
            """
        
        day_high_patch = 0 if extra_call.iloc[2] == 'N/A' else float(extra_call.iloc[2])
        day_low_patch = 0 if extra_call.iloc[3] == 'N/A' else float(extra_call.iloc[3])
        prev_close_patch = 0 if extra_call.iloc[5] == 'N/A' else float(extra_call.iloc[5])
        open_patch = 0 if extra_call.iloc[6] == 'N/A' else float(extra_call.iloc[6])
        tick_patch = 0 if len(extra_call.iloc[8]) == 0 else int(extra_call.iloc[8])
        contract_high_patch = 0 if extra_call.iloc[13] == 'N/A' else float(extra_call.iloc[13])
        contract_low_patch = 0 if extra_call.iloc[14] == 'N/A' else float(extra_call.iloc[14])

        extra_call_contract_data = {
            'id': call_options_chain_id,
            'call_options_chain_id': call_options_chain_id,
            'contract_name': contract_name,
            'delta': float(extra_call.iloc[16]),
            'gamma': float(extra_call.iloc[17]),
            'theta': float(extra_call.iloc[19]),
            'vega': float(extra_call.iloc[20]),
            'rho': float(extra_call.iloc[18]),
            'day_high': day_high_patch,
            'day_low': day_low_patch,
            'prev_close': prev_close_patch,
            'open': open_patch,
            'tick': tick_patch,
            'bid_size': int(extra_call.iloc[11]),
            'ask_size': int(extra_call.iloc[12]),
            'contract_high': contract_high_patch,
            'contract_low': contract_low_patch,
            'market': extra_call.iloc[15],
            'days_until_expiration': days_until_expiration,
            'volume': volume, 
            'open_interest': oi,
            'implied_volatility': impvol
        }

        cur.execute(insert_postgresql, extra_call_contract_data)
        conn.commit()

        print(f'Greeks and additional information of {symbol} added into PostgreSQL database "options_research"')

        cur.close()
        conn.close()

        
    def front_month_put_options(self):
        symbol = self.ticker

        put_options_chain_id = 0

        if self.exp_date != None:
           print(f'Researching {symbol} on {self.exp_date}')

           call_contract = options.get_options_chain(symbol, self.exp_date)['puts']
           self.inject_options_data(call_contract, 'put', put_options_chain_id, symbol, self.exp_date)

           return

        exp_date = options.get_expiration_dates(symbol)

        for date in exp_date:
            print(f'Researching {symbol} on {date}')

            splitted_date = date.split(' ')

            if int(splitted_date[-1]) == self.current_year and splitted_date[0] == self.current_month:
                date = ' '.join(splitted_date)
                put_contract = options.get_options_chain(symbol, date)['puts']

                self.inject_options_data(put_contract, 'put', put_options_chain_id, symbol, date)
            

    def front_month_put_extra(self, i, symbol, date, contract_name, put, strike, put_options_chain_id, volume, oi, impvol):
        print(f'Researching Greeks and additional information of {symbol} at {date} on row {i}')

        splitted_date = date.split(' ')

        day = int(splitted_date[1].replace(',', ''))
        days_until_expiration = day - self.current_day

        month_num = str(dt.strptime(splitted_date[0], '%B').month)
        if len(month_num) == 1:
            month_num = f'0{month_num}'
        
        day_num = str(day)
        if len(day_num) == 1: 
            day_num = f'0{day_num}'

        FOC_expiry_date = f'{splitted_date[-1]}-{month_num}-{day_num}'

        ref_FOC = FOC()
        contract_symbol = ref_FOC.get_contract_symbol(symbol, FOC_expiry_date, put, strike)
        fetch_contract_symbol_data = ref_FOC.get_options_price_data(contract_symbol)

        extra_call = fetch_contract_symbol_data.iloc[0]

        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        insert_postgresql = """ 
            INSERT INTO put_options_greeks (id, put_options_chain_id, contract_name, delta, gamma, theta, vega, rho, day_high, day_low, prev_close, open, tick, bid_size, ask_size, contract_high, contract_low, market, days_until_expiration, volume, open_interest, implied_volatility)
            VALUES (%(put_options_chain_id)s, %(put_options_chain_id)s, %(contract_name)s, %(delta)s, %(gamma)s, %(theta)s, %(vega)s, %(rho)s, %(day_high)s, %(day_low)s, %(prev_close)s, %(open)s, %(tick)s, %(bid_size)s, %(ask_size)s, %(contract_high)s, %(contract_low)s, %(market)s, %(days_until_expiration)s, %(volume)s, %(open_interest)s, %(implied_volatility)s)
            """
        
        day_high_patch = 0 if extra_call.iloc[2] == 'N/A' else float(extra_call.iloc[2])
        day_low_patch = 0 if extra_call.iloc[3] == 'N/A' else float(extra_call.iloc[3])
        prev_close_patch = 0 if extra_call.iloc[5] == 'N/A' else float(extra_call.iloc[5])
        open_patch = 0 if extra_call.iloc[6] == 'N/A' else float(extra_call.iloc[6])
        tick_patch = 0 if len(extra_call.iloc[8]) == 0 else int(extra_call.iloc[8])
        contract_high_patch = 0 if extra_call.iloc[13] == 'N/A' else float(extra_call.iloc[13])
        contract_low_patch = 0 if extra_call.iloc[14] == 'N/A' else float(extra_call.iloc[14])

        extra_call_contract_data = {
            'id': put_options_chain_id,
            'put_options_chain_id': put_options_chain_id,
            'contract_name': contract_name,
            'delta': float(extra_call.iloc[16]),
            'gamma': float(extra_call.iloc[17]),
            'theta': float(extra_call.iloc[19]),
            'vega': float(extra_call.iloc[20]),
            'rho': float(extra_call.iloc[18]),
            'day_high': day_high_patch,
            'day_low': day_low_patch,
            'prev_close': prev_close_patch,
            'open': open_patch,
            'tick': tick_patch,
            'bid_size': int(extra_call.iloc[11]),
            'ask_size': int(extra_call.iloc[12]),
            'contract_high': contract_high_patch,
            'contract_low': contract_low_patch,
            'market': extra_call.iloc[15],
            'days_until_expiration': days_until_expiration,
            'volume': volume, 
            'open_interest': oi,
            'implied_volatility': impvol
        }

        cur.execute(insert_postgresql, extra_call_contract_data)
        conn.commit()

        print(f'Greeks and additional information of {symbol} added into PostgreSQL database "options_research"')

        cur.close()
        conn.close()


    # Inject options data into the SQL database
    def inject_options_data(self, contract, buying_method, options_chain_id, symbol, date):
        bm = buying_method

        # i will be used in iloc[i] to get the row of the current options chain
        for i in range(len(contract)):
            print(f'Researching row {i} on {symbol} at {date}')

            conn = psycopg2.connect(
                dbname = 'options_research',
                user = #your username,
                password = #your password,
                host = 'localhost',
                port = '5432'
            )

            cur = conn.cursor()

            options_chain_id = options_chain_id + 1

            if bm == 'call':
                insert_postgresql = """
                    INSERT INTO call_options_chain (id, symbol, contract_name, bid, ask, mid, premium, change, volume, open_interest, implied_volatility, expiry_date, strike, added_time)
                    VALUES (%(options_chain_id)s, 
                            %(contract_symbol)s, 
                            %(contract_name)s, 
                            %(contract_bid)s, 
                            %(contract_ask)s, 
                            %(contract_mid)s, 
                            %(contract_last_price)s,
                            %(contract_change)s, 
                            %(contract_volume)s, 
                            %(contract_open_interest)s, 
                            %(contract_impvol)s, 
                            %(contract_expiry_date)s, 
                            %(contract_strike)s, 
                            %(contract_added_date)s)
                    """
                
            elif bm == 'put':
                insert_postgresql = """
                    INSERT INTO put_options_chain (id, symbol, contract_name, bid, ask, mid, premium, change, volume, open_interest, implied_volatility, expiry_date, strike, added_time)
                    VALUES (%(options_chain_id)s, 
                            %(contract_symbol)s, 
                            %(contract_name)s, 
                            %(contract_bid)s, 
                            %(contract_ask)s, 
                            %(contract_mid)s, 
                            %(contract_last_price)s, 
                            %(contract_change)s, 
                            %(contract_volume)s, 
                            %(contract_open_interest)s, 
                            %(contract_impvol)s, 
                            %(contract_expiry_date)s, 
                            %(contract_strike)s, 
                            %(contract_added_date)s)
                    """
            
            # Some values may be missing and are replaced with a '-', which undermines the integrity of the dataset
            # Created a ternary if/else to patch this issue
            bid_patch = 0 if contract['Bid'].iloc[i] == '-' else float(contract['Bid'].iloc[i])
            ask_patch = 0 if contract['Ask'].iloc[i] == '-' else float(contract['Ask'].iloc[i])
            mid_patch = (bid_patch + ask_patch) / 2
            volume_patch = 0 if contract['Volume'].iloc[i] == '-' else int(contract['Volume'].iloc[i])
            open_interest_patch = 0 if contract['Open Interest'].iloc[i] == '-' else int(contract['Open Interest'].iloc[i])
            impvol_patch = float(contract['Implied Volatility'].iloc[i].replace(',', '').strip('%'))

            contract_data = {
                'options_chain_id': options_chain_id,
                'contract_symbol': symbol,
                'contract_name': contract['Contract Name'].iloc[i],
                'contract_bid': bid_patch,
                'contract_ask': ask_patch,
                'contract_mid': mid_patch,
                'contract_last_price': float(contract['Last Price'].iloc[i]),
                'contract_change': float(contract['Change'].iloc[i]),
                'contract_volume': volume_patch,
                'contract_open_interest': open_interest_patch,
                'contract_impvol': impvol_patch,
                'contract_expiry_date': date,
                'contract_strike': float(contract['Strike'].iloc[i]),
                'contract_added_date': f'{self.current_month}/{self.current_day}/{self.current_year}'
            }

            cur.execute(insert_postgresql, contract_data)
            conn.commit()

            print(f'{symbol} injected into PostgreSQL database "options_research"')

            if bm == 'call':
                # Call the function to fetch extra data on that options contract
                self.front_month_call_extra(i, symbol, date, contract['Contract Name'].iloc[i], 'CALL', contract['Strike'].iloc[i], options_chain_id, volume_patch, open_interest_patch, impvol_patch)
            elif bm == 'put':
                self.front_month_put_extra(i, symbol, date, contract['Contract Name'].iloc[i], 'PUT', contract['Strike'].iloc[i], options_chain_id, volume_patch, open_interest_patch, impvol_patch)

            cur.close()
            conn.close()


    # Everytime a user requests new information, we reset the options chains, greeks, and suggested strategies
    def truncate_database(self, buying_method):
        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        if buying_method == 'call':
            truncate_dataset = """
                ALTER TABLE call_options_greeks
                DROP CONSTRAINT call_options_greeks_call_options_chain_id_fkey;

                ALTER TABLE call_options_strategies
                DROP CONSTRAINT call_options_strategies_call_options_greeks_id_fkey;

                TRUNCATE call_options_chain;
                TRUNCATE call_options_greeks;
                TRUNCATE call_options_strategies;

                ALTER TABLE call_options_greeks
                ADD CONSTRAINT call_options_greeks_call_options_chain_id_fkey FOREIGN KEY(call_options_chain_id) REFERENCES call_options_chain(id);

                ALTER TABLE call_options_strategies
                ADD CONSTRAINT call_options_strategies_call_options_greeks_id_fkey FOREIGN KEY(call_options_greeks_id) REFERENCES call_options_greeks(id);
                """
            
        elif buying_method == 'put':
            truncate_dataset = """
                ALTER TABLE put_options_greeks 
                DROP CONSTRAINT put_options_greeks_put_options_chain_id_fkey;

                ALTER TABLE put_options_strategies 
                DROP CONSTRAINT put_options_strategies_put_options_greeks_id_fkey;

                TRUNCATE put_options_chain;
                TRUNCATE put_options_greeks; 
                TRUNCATE put_options_strategies;

                ALTER TABLE put_options_greeks 
                ADD CONSTRAINT put_options_greeks_put_options_chain_id_fkey FOREIGN KEY(put_options_chain_id) REFERENCES put_options_chain(id);

                ALTER TABLE put_options_strategies 
                ADD CONSTRAINT put_options_strategies_put_options_greeks_id_fkey FOREIGN KEY(put_options_greeks_id) REFERENCES put_options_greeks(id);
                """

        # Also drop the call_and_put_options_chain table because in options_application.py, if the user reruns the program
        # we can't CREATE TABLE call_and_put_options_chain when call_and_put_options_chain already exists
        elif buying_method == 'all':
            truncate_dataset = """
                ALTER TABLE call_options_greeks
                DROP CONSTRAINT call_options_greeks_call_options_chain_id_fkey;

                ALTER TABLE call_options_strategies
                DROP CONSTRAINT call_options_strategies_call_options_greeks_id_fkey;

                TRUNCATE call_options_chain;
                TRUNCATE call_options_greeks;
                TRUNCATE call_options_strategies;

                ALTER TABLE call_options_greeks
                ADD CONSTRAINT call_options_greeks_call_options_chain_id_fkey FOREIGN KEY(call_options_chain_id) REFERENCES call_options_chain(id);

                ALTER TABLE call_options_strategies
                ADD CONSTRAINT call_options_strategies_call_options_greeks_id_fkey FOREIGN KEY(call_options_greeks_id) REFERENCES call_options_greeks(id);

                
                ALTER TABLE put_options_greeks 
                DROP CONSTRAINT put_options_greeks_put_options_chain_id_fkey;

                ALTER TABLE put_options_strategies 
                DROP CONSTRAINT put_options_strategies_put_options_greeks_id_fkey;

                TRUNCATE put_options_chain;
                TRUNCATE put_options_greeks; 
                TRUNCATE put_options_strategies;

                ALTER TABLE put_options_greeks 
                ADD CONSTRAINT put_options_greeks_put_options_chain_id_fkey FOREIGN KEY(put_options_chain_id) REFERENCES put_options_chain(id);

                ALTER TABLE put_options_strategies 
                ADD CONSTRAINT put_options_strategies_put_options_greeks_id_fkey FOREIGN KEY(put_options_greeks_id) REFERENCES put_options_greeks(id);

                DROP TABLE IF EXISTS call_and_put_options_chain;
                """

        cur.execute(truncate_dataset)        
        conn.commit()


    # Fetches the expiration dates of the given ticker
    def lookup_expiration_dates(self):
        return options.get_expiration_dates(self.ticker)
    

    # An index is only needed when we connect the call and put options chain together (see options_application.py)
    def add_index(self):
        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        add_index = """
            CREATE INDEX call_options_chain_strike_idx
            ON call_options_chain (strike);

            CREATE INDEX put_options_chain_strike_idx
            ON put_options_chain (strike);
            """
        
        cur.execute(add_index)
        conn.commit()


    # Remove the index (if exists) from the call_and_put_options_chain table
    def remove_index(self):
        conn = psycopg2.connect(
            dbname = 'options_research',
            user = #your username,
            password = #your password,
            host = 'localhost',
            port = '5432'
        )

        cur = conn.cursor()

        remove_index = """
            DROP INDEX IF EXISTS call_options_chain_strike_idx;

            DROP INDEX IF EXISTS put_options_chain_strike_idx;
            """
        
        cur.execute(remove_index)
        conn.commit()
