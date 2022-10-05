from tabnanny import check
from flask import Flask, session, request, redirect, render_template, url_for
from flask_session import Session
import sqlite3

from helpers import login_required, apology, cash_value, cash_display
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

app.jinja_env.filters["cash"] = cash_display

Session(app)

# Setup db connection
con = sqlite3.connect('cash-tracker.db', check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

@app.route('/')
@login_required
def index():
    return redirect(url_for('view_accounts'))

@app.route('/transactions')
@login_required
def transactions():
    return render_template('transactions.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # Ensure username was submitted
        if not request.form.get('username'):
            return apology('must provide username')

        # Ensure password was submitted
        elif not request.form.get('password'):
            return apology('must provide password')

        # Query database for username
        rows = cur.execute('SELECT * FROM users WHERE username = ?', 
                           (request.form.get('username'),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['password_hash'], 
                                                     request.form.get('password')):
            return apology('Invalid username and/or password')

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if password != confirmation:
            return apology("Passwords don't match")

        if not username:
            return apology('Please enter a username')

        if not password or not confirmation:
            return apology('Please enter a password')

        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                    (username, generate_password_hash(password)))
        con.commit()

        return redirect('/')


    else:
        return render_template('register.html')

@app.route('/create_owner', methods=['GET', 'POST'])
@login_required
def create_owner():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not first_name or not last_name:
            return apology('Please complete the details')

        cur.execute('INSERT INTO owners (first_name, last_name, user_id) VALUES (?, ?, ?)', 
                    (first_name, last_name, session['user_id']))
        con.commit()

        return redirect(url_for('view_owners'))

    return render_template('create_owner.html')

@app.route('/view_owners')
@login_required
def view_owners():
    owners = cur.execute("SELECT * FROM owners WHERE user_id = ?", (session['user_id'],)).fetchall()

    return render_template('view_owners.html', owners=owners)

@app.route('/edit_owner/<int:owner_id>', methods=['GET', 'POST'])
@login_required
def edit_owner(owner_id):
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not first_name or not last_name:
            return apology('Please enter first name and last name')

        cur.execute('UPDATE owners SET first_name = ?, last_name = ? WHERE id = ?', 
                    (first_name, last_name, owner_id))
        con.commit()

        return redirect(url_for('view_owners'))

    owner = cur.execute('SELECT * FROM owners WHERE id = ?', (owner_id,)).fetchall()
    return render_template('edit_owner.html', owner=owner[0])

@app.route('/delete_owner/<int:owner_id>', methods=['POST'])
@login_required
def delete_owner(owner_id):
    if request.method == 'POST':
        cur.execute('DELETE FROM owners WHERE id = ?', (owner_id,))
        con.commit()

        return redirect(url_for('view_owners'))


@app.route('/create_bank', methods=['GET', 'POST'])
@login_required
def create_bank():
    if request.method == 'POST':
        bank_name = request.form.get('name')
        account_number = request.form.get('account_number')

        cur.execute('INSERT INTO banks (name, account_number, user_id) VALUES (?, ?, ?)',
                    (bank_name, account_number, session['user_id']))
        con.commit()

        return redirect(url_for('view_banks'))

    return render_template('create_bank.html')

@app.route('/view_banks')
@login_required
def view_banks():
    banks = cur.execute("SELECT * FROM banks WHERE user_id = ?", (session['user_id'],)).fetchall()

    return render_template('view_banks.html', banks=banks)

@app.route('/edit_bank/<int:bank_id>', methods=['GET', 'POST'])
@login_required
def edit_bank(bank_id):
    if request.method == 'POST':
        name = request.form.get('name')
        account_number = request.form.get('account_number')
        
        if not name or not account_number:
            return apology('Please enter the required details')

        cur.execute('UPDATE banks SET name = ?, account_number = ? WHERE id = ?',
                    (name, account_number, bank_id))
        con.commit()

        return redirect(url_for('view_banks'))

    bank = cur.execute('SELECT * FROM banks WHERE id = ?', (bank_id,)).fetchall()
    return render_template('edit_bank.html', bank=bank[0])


@app.route('/delete_bank/<int:bank_id>', methods=['POST'])
@login_required
def delete_bank(bank_id):
    if request.method == 'POST':
        cur.execute('DELETE FROM banks WHERE id = ?', (bank_id,))
        con.commit()
    
    return redirect(url_for('view_banks'))


@app.route('/create_account', methods=['GET', 'POST'])
@login_required
def create_account():
    if request.method == 'POST':
        name = request.form.get('name')
        maintain = request.form.get('maintain')
        bank_id = int(request.form.get('bank'))
        owner_id = int(request.form.get('owner'))

        if not name:
            return apology('Please enter a name')

        if not maintain:
            maintain = cash_value(0)
        else:
            try:
                maintain = cash_value(maintain)
            except:
                return apology('Please enter a valid maintain amount')

        if bank_id == -1:
            return apology('Please select a valid bank')

        if owner_id == -1:
            return apology('Please select a valid owner')

        cur.execute('INSERT INTO accounts (name, maintain, user_id, bank_id, owner_id) VALUES (?, ?, ?, ?, ?)',
                    (name, maintain, session['user_id'], bank_id, owner_id))
        con.commit()

        return redirect(url_for('view_accounts'))
    
    banks = cur.execute('SELECT * FROM banks WHERE user_id = ?', (session['user_id'],)).fetchall()
    owners = cur.execute('SELECT * FROM owners WHERE user_id = ?', (session['user_id'],)).fetchall()

    return render_template('create_account.html', banks=banks, owners=owners)

@app.route('/view_accounts', methods=['GET'])
@login_required
def view_accounts():
    accounts = cur.execute("""SELECT a.id, 
                                (o.first_name || ' ' || o.last_name) AS owner_name, 
                                a.name AS account_name, 
                                b.name AS bank_name,
                                b.account_number AS bank_number,
                                IFNULL(SUM(t.amount), 0) AS actual_balance,
                                a.maintain,
                                IFNULL(SUM(t.amount), 0) - a.maintain AS available_balance
                            FROM accounts AS a 
                            INNER JOIN banks AS b ON a.bank_id = b.id
                            INNER JOIN owners AS o ON a.owner_id = o.id
                            LEFT JOIN transactions AS t ON t.account_id = a.id
                            WHERE a.user_id = ?
                            GROUP BY a.id
                            ORDER BY owner_name, account_name""", (session['user_id'],)).fetchall()

    return render_template('view_accounts.html', accounts=accounts)


@app.route('/edit_account/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    if request.method == 'POST':
        name = request.form.get('name')
        maintain = request.form.get('maintain')
        bank_id = int(request.form.get('bank'))
        owner_id = int(request.form.get('owner'))

        if not name:
            return apology('Please enter a name')

        if not maintain:
            maintain = cash_value(0)
        else:
            try:
                maintain = cash_value(maintain)
            except:
                return apology('Please enter a valid maintain amount')

        if bank_id == -1:
            return apology('Please select a valid bank')

        if owner_id == -1:
            return apology('Please select a valid owner')

        cur.execute('UPDATE accounts SET name = ?, maintain = ?, bank_id = ?, owner_id = ? WHERE id = ?', 
                    (name, maintain, bank_id, owner_id, account_id))
        con.commit()

        return redirect(url_for('view_accounts'))

    account = cur.execute("""SELECT a.*, 
                            b.id AS bank_id,
                            b.name AS bank_name,
                            b.account_number AS bank_number,
                            o.id AS owner_id,
                            (o.first_name || ' ' || o.last_name) AS owner_name
                          FROM accounts AS a 
                          INNER JOIN banks AS b ON a.bank_id = b.id
                          INNER JOIN owners AS o ON a.owner_id = o.id
                          WHERE a.id = ?""", (account_id,)).fetchall()
    banks = cur.execute("""SELECT * FROM banks
                        WHERE id NOT IN (SELECT bank_id FROM accounts WHERE id= ?)
                            AND user_id = ?""", (account_id, session['user_id'],)).fetchall()
    owners = cur.execute("""SELECT * FROM owners
                         WHERE id NOT IN (SELECT owner_id FROM accounts WHERE id = ?)
                            AND user_id = ?""", (account_id, session['user_id'],)).fetchall()

    return render_template('edit_account.html', account=account[0], banks=banks, owners=owners)

@app.route('/delete_account/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    if request.method == 'POST':
        cur.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        con.commit()

    return redirect(url_for('view_accounts'))


@app.route('/create_transaction/<type>', methods=['GET', 'POST'])
@login_required
def create_transaction(type):
    if request.method == 'POST':
        account = request.form.get('account')
        date = request.form.get('date')
        amount = cash_value(request.form.get('amount'))
        target = request.form.get('target')
        description = request.form.get('description')
    
        if type == 'income':
            cur.execute('INSERT INTO transactions (amount, description, date, target, account_id) VALUES (?, ?, ?, ?, ?)',
                        (amount, description, date, target, account))

        elif type == 'expense':
            amount = amount * -1
            cur.execute('INSERT INTO transactions (amount, description, date, target, account_id) VALUES (?, ?, ?, ?, ?)',
                        (amount, description, date, target, account))

        elif type == 'transfer':
            target_name = cur.execute("""SELECT a.name || ' (' || b.name || ' - ' || o.first_name || ' ' || o.last_name || ')' AS name
                                         FROM accounts AS a 
                                         INNER JOIN banks AS b ON a.bank_id = b.id
                                         INNER JOIN owners AS o ON a.owner_id = o.id
                                         WHERE a.id = ?""", (target,)).fetchone()[0]
            source_name = cur.execute("""SELECT a.name || ' (' || b.name || ' - ' || o.first_name || ' ' || o.last_name || ')' AS name
                                         FROM accounts AS a 
                                         INNER JOIN banks AS b ON a.bank_id = b.id
                                         INNER JOIN owners AS o ON a.owner_id = o.id
                                         WHERE a.id = ?""", (account,)).fetchone()[0]

            cur.execute('INSERT INTO transactions (amount, description, date, target, account_id) VALUES (?, ?, ?, ?, ?)',
                        ((amount * -1), description, date, target_name, account))
            cur.execute('INSERT INTO transactions (amount, description, date, target, account_id) VALUES (?, ?, ?, ?, ?)',
                        (amount, description, date, source_name, target))
        
        con.commit()
        return redirect(url_for('view_transactions'))

    accounts = cur.execute("""SELECT a.id, 
                                (o.first_name || ' ' || o.last_name) AS owner_name, 
                                a.name AS account_name, 
                                b.name AS bank_name
                            FROM accounts AS a 
                            INNER JOIN banks AS b ON a.bank_id = b.id
                            INNER JOIN owners AS o ON a.owner_id = o.id
                            WHERE a.user_id = ?
                            GROUP BY a.id
                            ORDER BY owner_name, account_name""", (session['user_id'],)).fetchall()

    return render_template('create_transaction.html', type=type, accounts=accounts)

@app.route('/view_transactions', methods=['GET'])
@login_required
def view_transactions():
    transactions = cur.execute("""SELECT t.id, 
                                   t.date,
                                   a.name AS account_name,
                                   (o.first_name || ' ' || o.last_name) AS owner,
                                   b.name AS bank_name,
                                   t.amount, 
                                   t.target, 
                                   t.description
                               FROM transactions AS t
                               INNER JOIN accounts AS a ON t.account_id = a.id
                               INNER JOIN banks AS b ON a.bank_id = b.id
                               INNER JOIN owners AS o ON a.owner_id = o.id
                               WHERE a.user_id = ?
                               ORDER BY t.date
                               """, (session['user_id'],)).fetchall()
    return render_template('view_transactions.html', transactions=transactions)

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    if request.method == 'POST':
        pass

    transaction = cur.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchall()
    return render_template('edit_transaction.html', transaction=transaction[0])

@app.route('/delete_transaction/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    pass