from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User  # Импорт модели User для проверки уникальности
import re


class RegistrationForm(FlaskForm):
	"""Форма регистрации нового пользователя.

	Поля:
			username (StringField): Имя пользователя (должно быть уникальным).
			email (StringField): Адрес электронной почты (должен быть уникальным и в правильном формате).
			password (PasswordField): Пароль для учетной записи.
			submit (SubmitField): Кнопка отправки формы.
	"""
	username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Зарегистрироваться')

	def validate_username(self, username):
		"""Проверка уникальности имени пользователя.

		Args:
				username (StringField): Имя пользователя для проверки.

		Raises:
				ValidationError: Если имя пользователя уже занято.
		"""
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')

	def validate_email(self, email):
		"""Проверка уникальности email.

		Args:
				email (StringField): Email для проверки.

		Raises:
				ValidationError: Если email уже зарегистрирован.
		"""
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Этот email уже зарегистрирован. Пожалуйста, используйте другой.')

	def validate_password(self, password):
		"""Проверка сложности пароля.

		Args:
				password (str): Пароль для проверки.

		Raises:
				ValidationError: Если пароль не соответствует требованиям.
		"""
		password_data = password.data
		if len(password_data) < 8:
			raise ValidationError('Пароль должен содержать не менее 8 символов.')
		if not re.search(r"[A-Z]", password_data):
			raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву.')
		if not re.search(r"[a-z]", password_data):
			raise ValidationError('Пароль должен содержать хотя бы одну строчную букву.')
		if not re.search(r"[0-9]", password_data):
			raise ValidationError('Пароль должен содержать хотя бы одну цифру.')
		if not re.search(r"[!@#$%^&*()?{}|<>-]", password_data):
			raise ValidationError('Пароль должен содержать хотя бы один специальный символ. (!@#$%^&*()?{}|<>)')


class LoginForm(FlaskForm):
	"""Форма входа пользователя.

	Поля:
			email (StringField): Адрес электронной почты для входа.
			password (PasswordField): Пароль для входа.
			submit (SubmitField): Кнопка отправки формы.
	"""
	username = StringField('Имя пользователя', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	submit = SubmitField('Войти')


class PostForm(FlaskForm):
	"""Форма создания нового поста.

	Поля:
			title (StringField): Заголовок поста.
			content (TextAreaField): Содержимое поста.
			submit (SubmitField): Кнопка отправки формы.
	"""
	title = StringField('Заголовок', validators=[DataRequired(), Length(min=1, max=200)])
	content = TextAreaField('Содержимое', validators=[DataRequired()])
	submit = SubmitField('Создать пост')


class EditForm(FlaskForm):
	"""Форма редактирования существующего поста.

	Поля:
			title (StringField): Заголовок поста.
			content (TextAreaField): Содержимое поста.
			submit (SubmitField): Кнопка отправки формы.
	"""
	title = StringField('Заголовок', validators=[DataRequired(), Length(min=1, max=200)])
	content = TextAreaField('Содержимое', validators=[DataRequired()])
	submit = SubmitField('Редактировать пост')


class ProfileForm(FlaskForm):
	"""Форма редактирования профиля пользователя.

	Поля:
			username (StringField): Имя пользователя.
			avatar (FileField): Аватар пользователя (необязательно).
			submit (SubmitField): Кнопка отправки формы.
	"""
	username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
	avatar = FileField('Аватар (необязательно)')
	submit = SubmitField('Обновить профиль')
