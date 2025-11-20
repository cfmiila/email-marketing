from flask import Flask, request, jsonify
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from database import add_email, get_emails
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

@app.route('/')
def home():
    return app.send_static_file('index.html')

scheduler = BackgroundScheduler()
scheduler.start()


@app.route('/status')
def status():
    return jsonify({
        "message": "Email Marketing API is running!",
        "routes": [
            "/add_email  (POST)",
            "/send_email  (POST)",
            "/schedule_email  (POST)",
            "/generate_report  (GET)"
        ]
    })



@app.route('/add_email', methods=['POST'])
def add_email_route():
    data = request.get_json()

    if not data or "email" not in data:
        return jsonify({"error": "Campo 'email' é obrigatório"}), 400

    sucesso, mensagem = add_email(data["email"])

    if sucesso:
        return jsonify({"message": mensagem}), 201
    else:
        return jsonify({"error": mensagem}), 400



def send_email_function(to, subject, body):
    try:
        message = Mail(
            from_email=os.getenv("FROM_EMAIL", "no-reply@example.com"),
            to_emails=to,
            subject=subject,
            html_content=body
        )

        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)

        return True

    except Exception as e:
        print("Erro ao enviar email:", e)
        return False



@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.get_json()

    required_fields = ["to", "subject", "body"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Campos 'to', 'subject' e 'body' são obrigatórios"}), 400

    success = send_email_function(data['to'], data['subject'], data['body'])

    if success:
        return jsonify({"message": "Email enviado com sucesso!"})
    else:
        return jsonify({"error": "Erro ao enviar email"}), 500



def schedule_email(to, subject, body, run_date):
    scheduler.add_job(
        send_email_function,
        args=[to, subject, body],
        trigger='date',
        run_date=run_date
    )


@app.route('/schedule_email', methods=['POST'])
def schedule_route():
    data = request.get_json()

    required = ["to", "subject", "body", "run_date"]
    if not data or not all(item in data for item in required):
        return jsonify({"error": "Campos 'to', 'subject', 'body', 'run_date' são obrigatórios"}), 400

    schedule_email(data['to'], data['subject'], data['body'], data['run_date'])
    return jsonify({"message": "Email agendado com sucesso!"})



@app.route('/generate_report', methods=['GET'])
def generate_report():
    emails = get_emails()

    df = pd.DataFrame(emails, columns=['ID', 'Email'])
    df.to_csv('report.csv', index=False)

    return jsonify({"message": "Relatório gerado"})


if __name__ == '__main__':
    app.run(debug=False)
