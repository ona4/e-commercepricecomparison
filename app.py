import requests
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite3'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column("User_ID", db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Weather(db.Model):
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=True)

def get_temperature():
    try:
        latitude = 40.0150
        longitude = -105.2705
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["current_weather"]["temperature"]
    except requests.RequestException as e:
        print(f"API request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"JSON parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

@app.route("/")
def main():
    return '''
     <form action="/echo_user_input" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    new_user = Users(name=input_text)
    db.session.add(new_user)
    current_temperature = get_temperature()
    if current_temperature is not None:
        existing_weather = Weather.query.filter_by(datetime=datetime.utcnow()).first()
        if existing_weather:
            existing_weather.temperature = current_temperature
        else:
            new_weather = Weather(temperature=current_temperature)
            db.session.add(new_weather)

    db.session.commit()
    all_users = Users.query.all()
    all_weather = Weather.query.order_by(Weather.datetime.desc()).limit(5).all()

    user_list = "".join([f"""
        <tr>
            <td>User {user.id}: {user.name}</td>
            <td>
                <form action="/delete_user/{user.id}" method="POST">
                    <input type="submit" value="Delete">
                </form>
            </td>
        </tr>
    """ for user in all_users])

    weather_list = "<br>".join([f"Date: {w.datetime}, Temperature: {w.temperature}°C" for w in all_weather])
    temperature_info = f"Current Temperature: {current_temperature}°C" if current_temperature is not None else "Temperature data unavailable. Please check the server logs for more information."

    return f"""
    <h2>You entered: {input_text}</h2>
    <h3>All Users:</h3>
    <table>
        {user_list}
    </table>
    <h3>Recent Weather Data:</h3>
    <p>{weather_list}</p>
    <p>{temperature_info}</p>
    <a href="/">Back to form</a>
    """

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
