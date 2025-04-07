from flask import Flask, render_template, redirect, session, url_for, request, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Nastavte tajný klíč pro relace

# Připojení k databázi
mydb = mysql.connector.connect(
    host="dbs.spskladno.cz",
    user="student10",
    password="spsnet",
    database="vyuka10"
)

@app.route('/registrace', methods=['GET', 'POST'])
def registrace():
    # Pokud je uživatel přihlášen, přesměruj ho na stránku "O hře"
    if 'user_id' in session:
        return redirect(url_for('o_hre'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            mycursor = mydb.cursor()
            # Zkontroluj, zda uživatelské jméno již existuje
            query_check = "SELECT ID FROM UsersMaze WHERE Username = %s"
            mycursor.execute(query_check, (username,))
            result = mycursor.fetchone()

            if result:
                flash('Uživatelské jméno již existuje. Zvolte jiné.', 'error')
            else:
                # Vložení nového uživatele do databáze
                query_insert = "INSERT INTO UsersMaze (Username, Password) VALUES (%s, %s)"
                mycursor.execute(query_insert, (username, password))
                mydb.commit()
                flash('Registrace byla úspěšná!', 'success')
                return redirect(url_for('prihlaseni'))  # Přesměrování na přihlášení
        except mysql.connector.Error as err:
            flash(f"Chyba při připojení k databázi: {err}", 'error')

    return render_template('registrace.html')

@app.route('/prihlaseni', methods=['GET', 'POST'])
def prihlaseni():
    if 'user_id' in session:
        return redirect(url_for('o_hre'))  # Přesměruj na stránku "O hře", pokud je uživatel již přihlášen
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            mycursor = mydb.cursor()
            query = "SELECT ID, Admin FROM UsersMaze WHERE Username = %s AND Password = %s"
            mycursor.execute(query, (username, password))
            user = mycursor.fetchone()

            if user:
                session['user_id'] = user[0]  # Uložení ID uživatele do session
                session['is_admin'] = bool(user[1])  # Uložení informace o administrátorovi do session
                print(f"User logged in: {session}")  # Debug: Zkontrolujte obsah session
                flash('Přihlášení bylo úspěšné.', 'success')
                return redirect(url_for('o_hre'))  # Přesměrování na stránku "O hře"
            else:
                flash('Neplatné přihlašovací údaje.', 'error')
        except mysql.connector.Error as err:
            flash(f"Chyba při přihlašování: {err}", 'error')

    return render_template('prihlaseni.html')

@app.route('/scoreboard')
def scoreboard():
    # Zkontroluj, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('prihlaseni'))  # Přesměruj na přihlášení, pokud není přihlášen

    try:
        mycursor = mydb.cursor()
        query = """
            SELECT TimeMaze.Time, TimeMaze.Level
            FROM TimeMaze
            WHERE TimeMaze.UserID = %s
            ORDER BY TimeMaze.Level ASC
        """
        mycursor.execute(query, (user_id,))
        results = mycursor.fetchall()
        print(results)  # Debug: Zkontrolujte, zda `results` obsahuje správná data
        return render_template('scoreboard.html', scores=results)
    except mysql.connector.Error as err:
        return f"Error: {err}"

@app.route('/o_hre')
def o_hre():
    print(f"Session data: {session}")  # Debug: Zobrazí obsah session v konzoli
    return render_template('o_hre.html')

@app.route('/odhlaseni')
def odhlaseni():
    session.pop('user_id', None)  # Odstranění uživatele ze session
    flash('Byli jste úspěšně odhlášeni.', 'success')
    return redirect(url_for('prihlaseni'))  # Přesměrování na přihlášení

@app.route('/admhraci')
def admhraci():
    # Zkontroluj, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('prihlaseni'))  # Přesměruj na přihlášení, pokud není přihlášen

    try:
        mycursor = mydb.cursor()
        # Zkontroluj, zda je uživatel administrátor
        query_admin_check = "SELECT Admin FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_admin_check, (user_id,))
        is_admin = mycursor.fetchone()

        if not is_admin or not is_admin[0]:  # Pokud není admin
            flash('Nemáte oprávnění pro přístup na tuto stránku.', 'error')
            return redirect(url_for('scoreboard'))  # Přesměruj na scoreboard

        # Načti všechny sloupce z tabulky UsersMaze
        query_players = "SELECT ID, Username, Password, Admin FROM UsersMaze"
        mycursor.execute(query_players)
        players = mycursor.fetchall()

        return render_template('admhraci.html', players=players)
    except mysql.connector.Error as err:
        return f"Error: {err}"

@app.route('/admhrac/<int:idhrace>')
def player_records(idhrace):
    # Zkontroluj, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('prihlaseni'))  # Přesměruj na přihlášení, pokud není přihlášen

    try:
        mycursor = mydb.cursor()
        # Zkontroluj, zda je uživatel administrátor
        query_admin_check = "SELECT Admin FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_admin_check, (user_id,))
        is_admin = mycursor.fetchone()

        if not is_admin or not is_admin[0]:  # Pokud není admin
            flash('Nemáte oprávnění pro přístup na tuto stránku.', 'error')
            return redirect(url_for('scoreboard'))  # Přesměruj na scoreboard

        # Načti záznamy z tabulky TimeMaze pro konkrétního hráče
        query_records = "SELECT ID, Time, Level FROM TimeMaze WHERE UserID = %s"
        mycursor.execute(query_records, (idhrace,))
        records = mycursor.fetchall()

        return render_template('player_records.html', records=records, idhrace=idhrace)
    except mysql.connector.Error as err:
        return f"Error: {err}"

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    # Zkontroluj, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('prihlaseni'))  # Přesměruj na přihlášení, pokud není přihlášen

    try:
        mycursor = mydb.cursor()
        # Zkontroluj, zda je uživatel administrátor
        query_admin_check = "SELECT Admin FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_admin_check, (user_id,))
        is_admin = mycursor.fetchone()

        if not is_admin or not is_admin[0]:  # Pokud není admin
            flash('Nemáte oprávnění pro tuto akci.', 'error')
            return redirect(url_for('admhraci'))  # Přesměruj na seznam hráčů

        # Smaž záznamy hráče z tabulky TimeMaze
        query_delete_time = "DELETE FROM TimeMaze WHERE UserID = %s"
        mycursor.execute(query_delete_time, (player_id,))

        # Smaž hráče z tabulky UsersMaze
        query_delete_user = "DELETE FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_delete_user, (player_id,))

        mydb.commit()
        flash('Hráč a všechny jeho údaje byly úspěšně smazány.', 'success')
        return redirect(url_for('admhraci'))  # Přesměruj zpět na seznam hráčů
    except mysql.connector.Error as err:
        flash(f"Chyba při mazání hráče: {err}", 'error')
        return redirect(url_for('admhraci'))

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    # Zkontroluj, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('prihlaseni'))  # Přesměruj na přihlášení, pokud není přihlášen

    try:
        mycursor = mydb.cursor()
        # Zkontroluj, zda je uživatel administrátor
        query_admin_check = "SELECT Admin FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_admin_check, (user_id,))
        is_admin = mycursor.fetchone()

        if not is_admin or not is_admin[0]:  # Pokud není admin
            flash('Nemáte oprávnění pro tuto akci.', 'error')
            return redirect(url_for('scoreboard'))  # Přesměruj na scoreboard

        # Smaž záznam podle ID
        query_delete = "DELETE FROM TimeMaze WHERE ID = %s"
        mycursor.execute(query_delete, (record_id,))
        mydb.commit()

        flash('Záznam byl úspěšně smazán.', 'success')
        return redirect(request.referrer)  # Přesměruj zpět na předchozí stránku
    except mysql.connector.Error as err:
        flash(f"Chyba při mazání záznamu: {err}", 'error')
        return redirect(request.referrer)

@app.route('/toggle_admin/<int:player_id>', methods=['POST'])
def toggle_admin(player_id):
    # Zkontroluj, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('prihlaseni'))  # Přesměruj na přihlášení, pokud není přihlášen

    try:
        mycursor = mydb.cursor()
        # Zkontroluj, zda je uživatel administrátor
        query_admin_check = "SELECT Admin FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_admin_check, (user_id,))
        is_admin = mycursor.fetchone()

        if not is_admin or not is_admin[0]:  # Pokud není admin
            flash('Nemáte oprávnění pro tuto akci.', 'error')
            return redirect(url_for('admhraci'))  # Přesměruj na seznam hráčů

        # Získej aktuální stav Admin pro daného hráče
        query_get_admin = "SELECT Admin FROM UsersMaze WHERE ID = %s"
        mycursor.execute(query_get_admin, (player_id,))
        current_admin_status = mycursor.fetchone()

        if current_admin_status is not None:
            # Přepni stav Admin
            new_admin_status = not current_admin_status[0]
            query_toggle_admin = "UPDATE UsersMaze SET Admin = %s WHERE ID = %s"
            mycursor.execute(query_toggle_admin, (new_admin_status, player_id))
            mydb.commit()

            flash('Stav Admin byl úspěšně změněn.', 'success')
        else:
            flash('Hráč nebyl nalezen.', 'error')

        return redirect(url_for('admhraci'))  # Přesměruj zpět na seznam hráčů
    except mysql.connector.Error as err:
        flash(f"Chyba při změně stavu Admin: {err}", 'error')
        return redirect(url_for('admhraci'))
    
if __name__ == "__main__":
    app.run(debug=True)