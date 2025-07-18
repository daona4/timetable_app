from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Thay bằng key bí mật mạnh hơn
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Danh sách ngày nghỉ
HOLIDAYS = ['2025-09-01', '2025-09-02', '2025-09-16', '2025-10-18']

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def generate_sundays(start_date_str, end_date_str):
    """Tạo danh sách các ngày Chủ nhật giữa start_date và end_date"""
    start = datetime.strptime(start_date_str, '%Y-%m-%d')
    end = datetime.strptime(end_date_str, '%Y-%m-%d')
    sundays = []
    current = start
    while current <= end:
        if current.weekday() == 6:  # Chủ nhật
            sundays.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return sundays

def generate_schedule(start_date_str, end_date_str, selections, room, teacher, studentgroup):
    """Tạo lịch học dựa trên lựa chọn"""
    schedule = []
    session_number = 1
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    holidays = HOLIDAYS + generate_sundays(start_date_str, end_date_str)

    current_date = start_date
    while current_date <= end_date and session_number <= 32:
        if current_date.weekday() in [1, 3]:  # Thứ 3 (1) hoặc Thứ 5 (3)
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in holidays:
                week_num = (current_date - start_date).days // 7 + 1
                if str(week_num) in selections:
                    slots = [1, 2] if selections[str(week_num)] == '2' else [1] if selections[str(week_num)] == '1_tue' else [1, 2]
                    for slot in slots:
                        if session_number <= 32:
                            schedule.append({
                                'term': 'Summer 2025',
                                'day': date_str,
                                'slot': slot,
                                'room': room,
                                'teacher': teacher,
                                'subjectcode': 'MARK1295',
                                'sessionnumber': session_number,
                                'studentgroup1': studentgroup,
                                'Note': '',
                                'SlotType': 0,
                                'Type': 0,
                                'Coaching': ''
                            })
                            session_number += 1
        current_date += timedelta(days=1)

    return schedule

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User(user_id)
        login_user(user)
        return redirect('/')
    return '''
    <form method="POST">
        <label>User ID (Tên giảng viên):</label>
        <input type="text" name="user_id"><br><br>
        <button type="submit">Đăng nhập</button>
    </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    error = None
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        room = request.form['room']
        teacher = request.form['teacher']
        studentgroup = request.form['studentgroup']
        selections = {key.split('_')[1]: value for key, value in request.form.items() if key.startswith('week_')}

        try:
            # Kiểm tra và chuyển đổi chuỗi thành datetime
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            error = "Định dạng ngày không hợp lệ (YYYY-MM-DD)."
            weeks = [(i, f"Tuần {i}") for i in range(1, 25)]
            return render_template('index.html', weeks=weeks, error=error)

        schedule = generate_schedule(start_date, end_date, selections, room, teacher, studentgroup)
        if len(schedule) < 32:
            error = "Lịch không đủ 32 slots. Vui lòng chọn thêm tuần."
            weeks = [(i, f"Tuần {i}") for i in range(1, 25)]
            return render_template('index.html', weeks=weeks, error=error)

        df = pd.DataFrame(schedule)
        output_file = f'Timetable_{teacher}.xlsx'
        df.to_excel(output_file, index=False)
        return send_file(output_file, as_attachment=True)

    weeks = [(i, f"Tuần {i}") for i in range(1, 25)]
    return render_template('index.html', weeks=weeks, error=error)

if __name__ == '__main__':
    app.run(debug=True)