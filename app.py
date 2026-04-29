import os
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

@app.route('/')
def index():
    plants = Plant.query.filter_by(parent_id=None).all()
    return render_template('index.html', plants=plants)

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
    content = request.form.get('content')
    file = request.files.get('photo')
    
    filename = None
    if file and file.filename != '':
        if allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Attenzione: formato immagine non supportato. La nota è stata salvata senza foto.', 'warning')

    new_note = DiaryNote(content=content, image_path=filename, plant_id=plant.id)
    db.session.add(new_note)
    db.session.commit()
    
    if not file or (file and allowed_file(file.filename)):
        flash('Nota aggiunta al diario con successo!', 'success')
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
