from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import pandas as pd
from datetime import datetime

# Khởi tạo Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Thay bằng chuỗi bất kỳ

# Khởi tạo LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Dummy user loader (bạn có thể thay bằng kiểm tra từ file hoặc DB nếu muốn)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User(user_id)
        login_user(user)
        return redirect(url_for('index'))
    return '''
    <form method="POST">
        <label>User ID (Tên giảng viên):</label>
        <input type="text" name="user_id" required><br><br>
        <button type="submit">Đăng nhập</button>
    </form>
    '''

# Route đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Trang chính
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    error = None
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        room = request.form['room']
        teacher = current_user.id
        studentgroup = request.form['studentgroup']
        selections = {key.split('_')[1]: value for key, value in request.form.items() if key.startswith('week_')}

        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            error = "Định dạng ngày không hợp lệ (YYYY-MM-DD)."
            weeks = [(i, f"Tuần {i}") for i in range(1, 25)]
            return render_template('index.html', weeks=weeks, error=error)

        # ⚠️ Bạn cần định nghĩa hàm generate_schedule này ở nơi khác
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

# Chạy app trên Replit hoặc máy cá nhân
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
