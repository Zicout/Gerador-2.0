from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from gerador.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField("Nome de Usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[
                             DataRequired(), Length(6, 20)])
    passwordConfirm = PasswordField("Confirmar Senha", validators=[
                                    DataRequired(), EqualTo("password")])
    submitCriarConta = SubmitField("Criar Conta")

    def validate_email(self, email):
        email = Usuario.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError("E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.")
    
    def validate_user(self, username):
        usuario = Usuario.query.filter_by(username=username.data).first()

        if usuario:
            raise ValidationError("Usuário já cadastrado. Entre com seu e-mail ou faça um novo cadastro.")



class Login(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[
                             DataRequired(), Length(6, 20)])
    lembrarSenha = BooleanField("Lembrar Dados de Acesso")
    submitLogin = SubmitField("Login")

class FormEditarPerfil(FlaskForm):
    username = StringField("Nome de Usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(["jpg", "png", "gif"])])
    ferramenta_gerador_etiqueta = BooleanField("Gerador de Etiquetas")
    ferramenta_adiciona_logo = BooleanField("Adicionar Logo")
    submit_editar_perfil = SubmitField("Confirmar Edição")

    def validate_email(self, email):

        # verifica se mudou de email
        if current_user.email != email.data:
            email = Usuario.query.filter_by(email=email.data).first()
            
            # agora sim valida com os emails do banco de dados
            if email:
                raise ValidationError("Já existe um usuário com esse e-mail. Cadastre outro e-mail.")

class AdicionarLogo(FlaskForm):
    foto_upload = FileField('Foto que terá a logo adicionada', validators=[FileAllowed(["jpg", "png", "gif"])])
    logo_upload = FileField('Logo a ser adicionada', validators=[FileAllowed(["jpg", "png", "gif"])])
    submit_adicionar_logo = SubmitField("Confirmar Envio")

class FormCriarPost(FlaskForm):
    titulo = StringField("Título do Post", validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField("Escreva seu Post aqui", validators=[DataRequired()])
    submit_post = SubmitField("Criar Post")

class FormEditarPost(FlaskForm):
    titulo = StringField("Título do Post", validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField("Escreva seu Post aqui", validators=[DataRequired()])
    submit_post = SubmitField("Editar Post")


    



