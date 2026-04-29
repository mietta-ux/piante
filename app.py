import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Plant, DiaryNote
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'green-thumb-secret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'webp', 'bmp', 'HEIC', 'JPG', 'PNG'}

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext.lower() for ext in ALLOWED_EXTENSIONS]

def init_db():
    with app.app_context():
        db.create_all()
        if not Plant.query.first():
            # Initial data
            plant1 = Plant(
                name='Bonsai di Fico', 
                species='Ficus Carica', 
                watering_frequency=1,
                image_url='bonsai_fico.png'
            )
            plant3 = Plant(
                name='Fiori', 
                species='Mix Fiori', 
                watering_frequency=1,
                image_url='fiori.png'
            )
            
            # Categoria Erbe Aromatiche
            plant_aromatiche = Plant(
                name='Piante Aromatiche',
                species='Gruppo Erbe',
                watering_frequency=1,
                image_url='aromatiche.png'
            )
            db.session.add(plant1)
            db.session.add(plant3)
            db.session.add(plant_aromatiche)
            
            # Erbe Aromatiche (Figlie)
            erbe_tips = {
                'Menta': 'Perfetta in bevande fresche come Mojito, tè freddo, o per insaporire zucchine e dolci al cioccolato.',
                'Prezzemolo': 'Ideale su piatti a base di pesce, funghi, patate e per guarnire la pasta.',
                'Timo': 'Ottimo per carni arrosto, patate al forno, funghi e legumi.',
                'Rosmarino': 'Il re delle patate al forno, arrosti di carne, focacce e pane fatto in casa.',
                'Salvia': 'Classica con burro per condire ravioli e gnocchi, ottima anche con carni bianche.',
                'Alloro': 'Indispensabile per brodi, stufati, legumi e sughi a lunga cottura.',
                'Erba cipollina': 'Perfetta per insaporire formaggi spalmabili, uova, patate e insalate fresche.',
                'Origano': 'Immancabile sulla pizza, caprese, insalate di pomodori e carne alla pizzaiola.',
                'Maggiorana': 'Delicata, perfetta per minestre, frittate, ripieni di carne e verdure delicate.'
            }
            for erba, tip in erbe_tips.items():
                nuova_erba = Plant(
                    name=erba,
                    species='Erba Aromatica',
                    watering_frequency=1,
                    image_url='aromatiche.png',
                    parent=plant_aromatiche,
                    tips=tip
                )
                db.session.add(nuova_erba)
                
            db.session.commit()

def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=45.918&longitude=10.884&current_weather=true"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            data = r.json()
            temp = data['current_weather']['temperature']
            wcode = data['current_weather']['weathercode']
            
            is_alert = temp < 5.0 or wcode >= 61
            
            if wcode == 0: condition = "Sereno"
            elif wcode in [1, 2, 3]: condition = "Nuvoloso"
            elif wcode in [45, 48]: condition = "Nebbia"
            elif wcode in [51, 53, 55]: condition = "Pioggerellina"
            elif wcode in [61, 63, 65]: condition = "Pioggia"
            elif wcode in [71, 73, 75]: condition = "Neve"
            elif wcode >= 95: condition = "Temporale"
            else: condition = "Variabile"

            message = f"Attenzione: clima critico per le piante all'aperto!" if is_alert else "Condizioni ottimali per le tue piante."
            
            return {
                'temp': temp,
                'condition': condition,
                'is_alert': is_alert,
                'message': message
            }
    except:
        pass
    return None

@app.route('/')
def index():
    plants = Plant.query.filter_by(parent_id=None).all()
    weather = get_weather()
    return render_template('index.html', plants=plants, weather=weather)

@app.route('/plant/<int:id>')
def plant_detail(id):
    plant = Plant.query.get_or_404(id)
    # Order notes by date descending for timeline
    notes = DiaryNote.query.filter_by(plant_id=id).order_by(DiaryNote.date_added.desc()).all()
    return render_template('plant_detail.html', plant=plant, notes=notes, now=datetime.utcnow())

@app.route('/plant/<int:id>/water', methods=['POST'])
def water_plant(id):
    plant = Plant.query.get_or_404(id)
    plant.last_watered = datetime.utcnow()
    db.session.commit()
    flash(f'{plant.name} è stata annaffiata!', 'success')
    return redirect(url_for('plant_detail', id=id))

@app.route('/plant/<int:id>/add_note', methods=['POST'])
def add_note(id):
    plant = Plant.query.get_or_404(id)
    content = request.form.get('content', '').strip()
    stress_before = request.form.get('stress_before', type=int)
    stress_after = request.form.get('stress_after', type=int)
    file = request.files.get('photo')
    
    filename = None
    if file and file.filename != '':
        if allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Attenzione: formato immagine non supportato.', 'warning')

    if not content and not filename and stress_before is None and stress_after is None:
        flash('Devi aggiungere almeno un testo, una foto o il livello di stress per pubblicare.', 'warning')
        return redirect(url_for('plant_detail', id=id))

    new_note = DiaryNote(
        content=content, 
        image_path=filename, 
        plant_id=plant.id,
        stress_before=stress_before,
        stress_after=stress_after
    )
    db.session.add(new_note)
    db.session.commit()
    
    if not file or (file and allowed_file(file.filename)):
        flash('Nota aggiunta al diario con successo!', 'success')
    return redirect(url_for('plant_detail', id=id))

@app.route('/plant/<int:id>/quick_action', methods=['POST'])
def quick_action(id):
    plant = Plant.query.get_or_404(id)
    action = request.form.get('action')
    if action:
        note = DiaryNote(content=f"🛠 Intervento a lungo termine: {action}", plant_id=plant.id)
        db.session.add(note)
        db.session.commit()
        flash(f'Intervento "{action}" registrato nel diario!', 'success')
    return redirect(url_for('plant_detail', id=id))

@app.route('/note/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    note = DiaryNote.query.get_or_404(note_id)
    plant_id = note.plant_id
    db.session.delete(note)
    db.session.commit()
    flash('Nota eliminata!', 'success')
    return redirect(url_for('plant_detail', id=plant_id))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
