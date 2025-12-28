from flask import Flask, render_template, session, request, redirect, url_for
import secrets
import datetime
import scripts.api

import qrcode
from io import BytesIO
import base64

from scripts.calculo_de_probabilidad import *

app = Flask(__name__)
app.secret_key = b'%s' % secrets.token_bytes()
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=60)

@app.route('/')
def index():
    players = session.get('players')
    return render_template('index.html', players=players)

@app.route('/add-player', methods = ['POST'])
def add_player():
    name = request.form.get('name')
    surname1 = request.form.get('surname1')
    surname2 = request.form.get('surname2')

    players = session.get('players')
    if not players:
        players = []
    players.append({
            'name': name,
            'surname1': surname1,
            'surname2': surname2
        })

    session['players'] = players
    session.permanent = True
    return redirect(url_for('index'))

@app.route('/delete-player', methods = ['POST'])
def delete_player():
    players = session.get('players')
    index = int(request.form.get('id'))
    players.pop(index)
    session['players'] = players
    session.permanent = True
    return redirect(url_for('index'))

@app.route('/get-players-from-form')
def get_players_from_form():
    form_id, form_url = scripts.api.crear_formulario()

    qr_img = qrcode.make(form_url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return render_template('get-players-from-form.html',qr_code=qr_base64, form_id=form_id)

@app.route('/extract-players', methods=['GET'])
def extract_players():
    players = scripts.api.obtener_respuestas(request.args.get('form_id'))
    session['players'] = players
    return redirect(url_for('index'))

@app.route('/display-probabilities')
def display_probabilities():
    players = session.get('players')
    if not players:
        return redirect(url_for('index'))
    else:
        print(players)
        player_list = []
        for p in players:
            player_list.append(Participante(p['surname1'], p['surname2'], p['name']))
            # Calcula las probabilidades de los participantes.
            # Dichas probabilidades quedan guardadas en los atributos de los objetos
            # Participante.
        calcular_probabilidades(player_list)
        probabilized_list = [
            {
                'surname1': p.primer_apellido,
                'surname2': p.segundo_apellido,
                'name': p.nombre,
                'prob': p.get_probabilidad()*100
            } for p in player_list
        ]
        probabilized_list.sort(key = lambda x : -x['prob'])
        print(probabilized_list)
        return render_template('display_probabilities.html', probabilized_list = probabilized_list)
    

if __name__ == "__main__":
    app.run(debug=True)

