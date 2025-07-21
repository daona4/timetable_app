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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    error = None
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        room = request.form['room']
        teacher = current_user.id  # Lấy teacher từ user_id đã đăng nhập
        studentgroup = request.form['studentgroup']
        selections = {key.split('_')[1]: value for key, value in request.form.items() if key.startswith('week_')}

        try:
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

# ✅ Chỉnh đúng cho Replit
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
