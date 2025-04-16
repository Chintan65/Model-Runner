from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json
import subprocess
import shutil

app = Flask(__name__)
UPLOAD_MODEL_FOLDER = 'uploaded_models'
UPLOAD_PARAMETER_FOLDER = 'uploaded_parameters'
GENERATED_IMAGE_FOLDER = 'static/generated_images'

app.config['UPLOAD_MODEL_FOLDER'] = UPLOAD_MODEL_FOLDER
app.config['UPLOAD_PARAMETER_FOLDER'] = UPLOAD_PARAMETER_FOLDER
app.config['GENERATED_IMAGE_FOLDER'] = GENERATED_IMAGE_FOLDER

model_data = {}
MODEL_DATA_FILE = 'model_data.json'
if os.path.exists(MODEL_DATA_FILE):
    with open(MODEL_DATA_FILE, 'r') as f:
        model_data = json.load(f)

def save_model_data():
    with open(MODEL_DATA_FILE, 'w') as f:
        json.dump(model_data, f, indent=4)


os.makedirs(UPLOAD_MODEL_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_PARAMETER_FOLDER, exist_ok=True)
os.makedirs(GENERATED_IMAGE_FOLDER, exist_ok=True)

def get_available_models():
    return [f for f in os.listdir(app.config['UPLOAD_MODEL_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_MODEL_FOLDER'], f))]

def get_associated_parameter_file(model_filename):
    return model_data.get(model_filename, {}).get('parameter_filename')

@app.route('/')
def homepage():
    available_models = get_available_models()
    return render_template('homepage.html', available_models=available_models, model_data=model_data)

@app.route('/model_upload', methods=['GET', 'POST'])
def model_upload():
    if request.method == 'POST':
        if 'model_file' not in request.files:
            return 'No file part'
        file = request.files['model_file']
        model_name = request.form.get('model_name')
        if file.filename == '':
            return 'No selected file'
        if file:
            model_filename = file.filename
            model_path = os.path.join(app.config['UPLOAD_MODEL_FOLDER'], model_filename)
            file.save(model_path)
            model_data[model_filename] = {'name': model_name if model_name else model_filename, 'parameter_filename': None}
            save_model_data()
            return redirect(url_for('parameter_upload', model_filename=model_filename))
    return render_template('model_upload.html')

@app.route('/parameter_upload', methods=['GET', 'POST'])
def parameter_upload():
    model_filename = request.args.get('model_filename')
    if model_filename is None:
        return redirect(url_for('model_upload'))

    parameter_data = None
    if request.method == 'POST':
        if 'parameter_file' not in request.files:
            return 'No file part'
        file = request.files['parameter_file']
        if file.filename == '':
            return 'No selected file'
        if file:
            parameter_filename = file.filename
            parameter_path = os.path.join(app.config['UPLOAD_PARAMETER_FOLDER'], parameter_filename)
            file.save(parameter_path)

            model_data[model_filename]['parameter_filename'] = parameter_filename
            save_model_data()

            try:
                with open(parameter_path, 'r') as f:
                    parameter_data = json.load(f)
            except json.JSONDecodeError:
                parameter_data = {"error": "Invalid JSON file."}
            except FileNotFoundError:
                parameter_data = {"error": "Could not read the uploaded file."}

            return render_template('parameter_upload_preview.html', model_filename=model_filename, parameter_data=parameter_data, parameter_filename=parameter_filename)

    return render_template('parameter_upload.html', model_filename=model_filename)

@app.route('/run_model', methods=['GET', 'POST'])
def run_model():
    model_filename = request.args.get('model_filename')
    parameter_filename = request.args.get('parameter_filename')

    if model_filename is None:
        return redirect(url_for('homepage'))

    if parameter_filename is None:
        parameter_filename = get_associated_parameter_file(model_filename)
        if parameter_filename:
            return redirect(url_for('run_model', model_filename=model_filename, parameter_filename=parameter_filename))
        else:
            return render_template('run_model_no_params.html', model_filename=model_filename)

    parameter_path = os.path.join(app.config['UPLOAD_PARAMETER_FOLDER'], parameter_filename)
    try:
        with open(parameter_path, 'r') as f:
            model_parameters = json.load(f)
    except FileNotFoundError:
        return 'Parameter file not found.'
    except json.JSONDecodeError:
        return 'Invalid JSON parameter file.'

    input_parameters = model_parameters.get('input_parameters', [])

    if request.method == 'POST':
        user_input = request.form.to_dict()
        model_path = os.path.join(app.config['UPLOAD_MODEL_FOLDER'], model_filename)
        command = ['python', model_path]

        for param in input_parameters:
            name = param.get('name')
            if name and name in user_input:
                command.extend([f"--{name}", user_input[name]])

        try:
            result = subprocess.run(command, capture_output=True, check=True)
            # result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            error = result.stderr.strip()

            try:
                output_json = json.loads(output)
                return render_template('output.html', output_json=output_json, error=error,
                                       model_filename=model_filename, parameter_filename=parameter_filename)
            except json.JSONDecodeError:
                try:
                    output_number = float(output)
                    return render_template('output.html', output_number=output_number, error=error,
                                           model_filename=model_filename, parameter_filename=parameter_filename)
                except ValueError:
                    if any(output.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']) and os.path.exists(output):
                        image_name = os.path.basename(output)
                        target_path = os.path.join(app.config['GENERATED_IMAGE_FOLDER'], image_name)
                        shutil.copyfile(output, target_path)
                        return render_template('output.html', output_image_filename=image_name, error=error,
                                               model_filename=model_filename, parameter_filename=parameter_filename)
                    else:
                        return render_template('output.html', output_text=output, error=error,
                                               model_filename=model_filename, parameter_filename=parameter_filename)

        except subprocess.CalledProcessError as e:
            output = f"Error running model: {e}\n{e.stderr}"
            return render_template('output.html', output_text=output, error=e.stderr,
                                   model_filename=model_filename, parameter_filename=parameter_filename)
        except FileNotFoundError:
            return render_template('output.html', output_text="Model file not found.", error="Model file not found.",
                                   model_filename=model_filename, parameter_filename=parameter_filename)

    return render_template('run_model.html', input_parameters=input_parameters, model_filename=model_filename, parameter_filename=parameter_filename)

@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['GENERATED_IMAGE_FOLDER'], filename)

@app.route('/output')
def output_page():
    output_text = request.args.get('output_text', '')
    output_json = None
    try:
        output_json = json.loads(request.args.get('output_json', ''))
    except json.JSONDecodeError:
        pass
    error = request.args.get('error', '')
    return render_template('output.html', output_text=output_text, output_json=output_json, error=error)

if __name__ == '__main__':
    app.run(debug=True)
