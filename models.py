from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
	"""Модель пользователя.

	Атрибуты:
			id (int): Уникальный идентификатор пользователя.
			username (str): Имя пользователя (должно быть уникальным).
			email (str): Адрес электронной почты пользователя (должен быть уникальным).
			password (str): Хэшированный пароль пользователя.
			avatar (str): Путь к аватару пользователя (по умолчанию 'default.jpg').

	Связи:
			posts (list): Список постов, созданных пользователем.
	"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), nullable=False, unique=True)
	email = db.Column(db.String(150), nullable=False, unique=True)
	password = db.Column(db.String(150), nullable=False)
	avatar = db.Column(db.String(150), default='default.jpg')

	# Связь один-ко-многим с каскадным удалением: при удалении пользователя все его посты также будут удалены.
	posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")

	def set_password(self, password):
		"""Установка пароля пользователя с хэшированием.

				Args:
						password (str): Пароль, который нужно установить для пользователя.
		"""
		self.password = generate_password_hash(password)

	def check_password(self, password):
		"""Проверка пароля пользователя.

				Args:
						password (str): Пароль для проверки.

				Returns:
						bool: True, если пароль совпадает; иначе False.
		"""
		return check_password_hash(self.password, password)


class Post(db.Model):
	"""Модель поста.

			Атрибуты:
					id (int): Уникальный идентификатор поста.
					title (str): Заголовок поста.
					content (str): Содержимое поста.
					author_id (int): Идентификатор автора поста (ссылается на модель User).

			Связи:
					author (User): Автор поста.
	"""
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text, nullable=False)

	# Внешний ключ: идентификатор автора поста.
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
