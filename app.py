import os
from flask import Flask
from flask import render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm, PostForm, ProfileForm, EditForm  # Импорт форм.
from models import db, User, Post

# Инициализация приложения и конфигурация базы данных.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['UPLOAD_FOLDER'] = 'static/avatars'

# Инициализация базы данных и менеджера входа.
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
	"""Загрузка пользователя по ID.

		Args:
				user_id (int): Уникальный идентификатор пользователя.

		Returns:
				User: Объект пользователя или None.
	"""
	return User.query.get(int(user_id))


@app.route('/', methods=['GET'])
def index():
	"""Главная страница с отображением всех постов.

		Returns:
				str: Отрендеренный HTML шаблон главной страницы.
	"""
	posts = Post.query.all()
	return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Регистрация нового пользователя.

		Returns:
				str: Отрендеренный HTML шаблон страницы регистрации.
	"""
	form = RegistrationForm()

	if form.validate_on_submit():
		new_user = User(
			username=form.username.data,
			email=form.email.data
		)
		new_user.set_password(form.password.data)

		db.session.add(new_user)
		db.session.commit()
		flash('Регистрация прошла успешно! Пожалуйста, войдите.', 'success')
		return redirect(url_for('login'))

	return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Вход пользователя в систему.

		Returns:
				str: Отрендеренный HTML шаблон страницы входа.
	"""
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and user.check_password(form.password.data):
			login_user(user)
			return redirect(url_for('index'))

		flash('Неудачный вход. Проверьте ваш username и пароль.', 'danger')

	return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	"""Выход пользователя из системы.

		Returns:
				str: Перенаправление на страницу входа.
	"""
	logout_user()
	return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	"""Редактирование профиля пользователя.

		Returns:
				str: Отрендеренный HTML шаблон страницы профиля.
	"""
	form = ProfileForm()

	if form.validate_on_submit():
		current_user.username = form.username.data

		# Обработка загрузки аватара.
		if form.avatar.data:
			avatar_filename = f"{current_user.id}_{form.avatar.data.filename}"
			avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
			form.avatar.data.save(avatar_path)
			current_user.avatar = avatar_filename

		db.session.commit()
		flash('Профиль обновлен успешно!', 'success')
		return redirect(url_for('profile'))

	return render_template('profile.html', form=form)


@app.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
	"""Удаление профиля пользователя.

		Returns:
				str: Перенаправление на главную страницу после удаления профиля.
	"""
	user_id = current_user.id

	# Удаляем профиль пользователя
	user = User.query.get_or_404(user_id)
	db.session.delete(user)
	db.session.commit()

	flash('Ваш профиль был успешно удалён.', 'success')
	logout_user()  # Выход из системы после удаления профиля
	return redirect(url_for('index'))


@app.route('/post/<int:post_id>', methods=['GET'])
def post_detail(post_id):
	"""Просмотр отдельного поста.

		Args:
				post_id (int): Уникальный идентификатор поста.

		Returns:
				str: Отрендеренный HTML шаблон страницы поста.
	"""
	post = Post.query.get_or_404(post_id)

	return render_template('post_detail.html', post=post)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
	"""Создание нового поста.

		Returns:
				str: Отрендеренный HTML шаблон страницы создания поста.
	"""
	form = PostForm()

	if form.validate_on_submit():
		new_post = Post(title=form.title.data,
										content=form.content.data,
										author_id=current_user.id)

		db.session.add(new_post)
		db.session.commit()

		flash('Пост создан успешно!', 'success')
		return redirect(url_for('index'))

	return render_template('create_post.html', form=form)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
	"""Редактирование существующего поста.

	Args:
		post_id (int): Уникальный идентификатор поста.

	Returns:
		str: Отрендеренный HTML шаблон страницы редактирования поста.
	"""
	post = Post.query.get_or_404(post_id)

	# Проверка прав доступа к редактированию поста.
	if post.author_id != current_user.id:
		flash('Вы не можете редактировать этот пост.', 'danger')
		return redirect(url_for('index'))

	form = EditForm(obj=post)

	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Пост обновлен успешно!', 'success')
		return redirect(url_for('post_detail', post_id=post.id))

	return render_template('edit_post.html', form=form, post=post)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
	"""Удаление поста.

	Args:
			post_id (int): Уникальный идентификатор поста.

	Returns:
			str: Перенаправление на главную страницу после удаления поста.
	"""
	post = Post.query.get_or_404(post_id)

	# Проверка прав доступа к удалению поста.
	if post.author_id != current_user.id:
		flash('Вы не можете удалить этот пост.', 'danger')
		return redirect(url_for('index'))

	db.session.delete(post)
	db.session.commit()

	flash('Пост был успешно удалён.', 'success')
	return redirect(url_for('index'))


if __name__ == '__main__':
	with app.app_context():
		db.create_all()  # Создание таблиц базы данных.

	app.run(debug=True)
