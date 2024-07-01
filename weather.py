from flask import Flask, render_template, request, flash
import requests
from datetime import datetime, timedelta
import babel.dates


def format_date(value, format='medium'):
    format = "d MMMM yyyy 'года'"
    return babel.dates.format_date(value, format, locale='ru')


app = Flask(__name__)
app.jinja_env.filters['datetime'] = format_date
app.secret_key = 'c8f468436b18f8443a99c1a7c07f5cdb'


@app.route('/', methods=['GET', 'POST'])
def home():
    now = datetime.now() + timedelta(hours=3)
    days = [now + timedelta(days=i) for i in range(6)]
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Пожалуйста, введите город.')
            return render_template('home.html', days=days)
        day = int(request.form.get('day', 0))
        response = requests.get(f'http://api.openweathermap.org/data/2.5/'
                                f'forecast?q={city}&appid=6b5b558a73b9db968ce1de7b26ffc7e9&lang=ru')
        weather = response.json()
        if 'message' in weather and weather['message'] == 'city not found':
            flash('Этого города здесь нет, попробуйте другой.')
            return render_template('home.html', days=days)

        # Отфильтровать прогнозы по выбранному дню
        selected_day = days[day].strftime('%Y-%m-%d')
        forecasts = [forecast for forecast in weather['list'] if forecast['dt_txt'].startswith(selected_day)]

        # Конвертируем температуру из кельвинов в градусы Цельсия и округляем до 1 знака после запятой
        for forecast in forecasts:
            forecast['main']['temp'] = round(forecast['main']['temp'] - 273.15, 1)

        return render_template('home.html', weather=weather, forecasts=forecasts, day=day, days=days)

    return render_template('home.html', days=days)


if __name__ == '__main__':
    app.run(debug=True)
