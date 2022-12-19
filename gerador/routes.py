from flask import render_template, redirect, url_for, flash, request
from gerador import app, database, bcrypt
from gerador.forms import FormCriarConta, Login, FormEditarPerfil, AdicionarLogo, FormCriarPost, FormEditarPost
from gerador.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template("home.html", posts=posts)


@app.route("/contato")
def contato():
    return "Entre em contato comigo cara"


@app.route("/usuarios")
@login_required
def usuarios():
    users = Usuario.query.all()
    return render_template("usuarios.html", users=users)


@app.route("/login", methods=["GET", "POST"])
def login():
    formLogin = Login()
    formCriarConta = FormCriarConta()

    # fez login
    if formLogin.validate_on_submit() and "submitLogin" in request.form:

        # obtem o usuario
        usuario = Usuario.query.filter_by(email=formLogin.email.data).first()

        # checa se o usuario está realmente logado
        if usuario and bcrypt.check_password_hash(usuario.password, formLogin.password.data):

            # loga usuário e manda mensagem para caso senha bem sucedido
            login_user(usuario, remember=formLogin.lembrarSenha.data)
            flash(
                f"Login efetuado com Sucesso na conta {formLogin.email.data}", "alert-success container")

            # verifica o parametro da URL para um redirecionamento inteligent(Se o usuário tentava ver uma página sem permissão, agora após o login ele será redirecionado automaticamente)
            par_next = request.args.get("next")

            if par_next:
                return redirect(par_next)

            else:
                return redirect(url_for("home"))

        else:
            flash("Falha no Login. E-mail ou senha incorretos.",
                  "alert-danger container")

    # cria conta com sucesso
    if formCriarConta.validate_on_submit() and "submitCriarConta" in request.form:

        with app.app_context():

            # senha criptografada
            senhaCriptografada = bcrypt.generate_password_hash(
                formCriarConta.password.data)

            # Obtém todos os dados necessários para inserir no DATABASE
            usuario = Usuario(username=formCriarConta.username.data,
                              email=formCriarConta.email.data, password=senhaCriptografada)

            # Adicionar a sessão
            database.session.add(usuario)

            # Commit na sessão
            database.session.commit()

        flash(f"Conta criada com Sucesso no e-mail {formCriarConta.email.data}", "alert-success container")

            
        return redirect(url_for("login"))

    return render_template("login.html", formLogin=formLogin, formCriarConta=formCriarConta)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f"Logout feito com Sucesso.", "alert-success container")
    return redirect(url_for("login"))


@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")


@app.route("/post/criar", methods=["GET", "POST"])
@login_required
def criar_post():
    form = FormCriarPost()

    if form.validate_on_submit():
        

        with app.app_context():
            post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
            database.session.add(post)
            database.session.commit()
        flash(f"Post criado com Sucesso", "alert-success container")

        return redirect(url_for("home"))


    return render_template("criarpost.html", form=form)


def foto_perfil():
    foto_perfil = url_for(
        "static", filename="fotos_perfil/{}".format(current_user.foto_perfil))
    return foto_perfil


@app.context_processor
def context_processor():
    return dict(key='value', foto_perfil=foto_perfil)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(
        app.root_path, "static/fotos_perfil", nome_arquivo)

    tamanho = (200, 200)

    # salva a imagem
    imagem_reduzida = Image.open(imagem)

    # reduz o tamanho da imagem
    imagem_reduzida.thumbnail(tamanho)

    # salva a imagem
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def atualizar_ferramentas(form):

    lista_ferramentas = []

    for campo in form:

        if "ferramenta_" in campo.name:
            if campo.data:
                lista_ferramentas.append(campo.label.text)

    return ";".join(lista_ferramentas)

@app.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form = FormEditarPerfil()

    if form.validate_on_submit():
        with app.app_context():
            current_user.email = form.email.data
            current_user.username = form.username.data

            if form.foto_perfil.data:  # a foto enviada pelo formulário está aqui.
                nome_imagem = salvar_imagem(form.foto_perfil.data)
                current_user.foto_perfil = nome_imagem
            
            current_user.ferramentas = atualizar_ferramentas(form)

            database.session.commit()
        flash(f"Perfil atualizado com sucesso.", "alert-success")
        return redirect(url_for('perfil'))

    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username

    return render_template("editarperfil.html", form=form, email_campo=current_user.email.split("@")[1])


def salvar_logo(imagem):

    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + extensao
    caminho_completo = os.path.join(app.root_path, "static", nome_arquivo)


    # salva a imagem
    imagem_correta = Image.open(imagem)

    # salva a imagem
    imagem_correta.save(caminho_completo)
    return caminho_completo

@app.route("/adicionar_logo", methods=["GET", "POST"])
def criar_logo():

    pasta = "./gerador/static"

    # apaga automaticamente as imagens geradas quando alguem entra na página a fim de evitar uma sobrexposição de imagens no servidor
    for diretorio, subpastas, arquivos in os.walk(pasta):
        if diretorio != "./gerador/static/fotos_perfil":
            for arquivo in arquivos:
                if ".jpg" in arquivo:
                    os.remove(os.path.join(
                        os.path.realpath(diretorio), arquivo))
                elif ".png" in arquivo:
                    os.remove(os.path.join(
                        os.path.realpath(diretorio), arquivo))
                elif ".gif" in arquivo:
                    os.remove(os.path.join(
                        os.path.realpath(diretorio), arquivo))

    form = AdicionarLogo()

    imagem = form.foto_upload.data

    if form.validate_on_submit():

        # verifica se foi preenchido
        if form.foto_upload.data:

            # salva e abre a imagem enviada
            caminho = salvar_logo(form.foto_upload.data)
            imagem = Image.open(caminho)

            # obtém o tamanho da imagem enviada
            tamanho = imagem.size
            width = tamanho[0]
            height = tamanho[1]
            tamanho = (0.30*imagem.size[0], 0.30*imagem.size[1])
       

            if form.logo_upload.data:
                # abrindo logo
                caminho_logo = salvar_logo(form.logo_upload.data) 
                logo = Image.open(caminho_logo)

                # reduz o tamanho da imagem
                logo.thumbnail(tamanho)


                # colando uma na outra e salvando a colagem
                imagem.paste(logo, (int(width - 0.30*(width)), int(height - 0.20*(height))-50), logo)
                #Image.Image.paste(imagem, logo, (int(width - 0.30*(width)), int(height - 0.20*(height))))
                #######imagem.paste(logo, logo)
                imagem.save(caminho)

                caminho_dividido = caminho.split("/")
                filename = caminho_dividido[len(caminho_dividido)-1]

                return render_template("vazio.html", filename=filename)
            
            else:
                flash(f"Você precisa adicionar a logo para continuar.", "alert-danger")

        else:
            flash(f"Você precisa adicionar uma imagem para continuar.", "alert-danger")


    return render_template("adicionar_logo.html", form=form)

@app.route("/post/<post_id>")
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)

    return render_template("post.html", post=post)


@app.route("/post/<post_id>/editar", methods=["GET", "POST"])
@login_required
def editar_post(post_id):
    post = Post.query.get(post_id)

    if post.autor == current_user:   

        if current_user == post.autor:
            form = FormEditarPost()                    

            if request.method == "GET":
                form.titulo.data = post.titulo
                form.corpo.data = post.corpo
            
            elif form.validate_on_submit():

                
                post.titulo = form.titulo.data
                post.corpo = form.corpo.data 
                    
                database.session.commit()
                
                return redirect(url_for("exibir_post", post_id=post_id))


        else:
            form = None

        return render_template("editarpost.html", post=post, form=form)

    else:
        flash("Você não pode editar posts que não foram criados por você!", "alert-danger container")

        return redirect(url_for("home"))

@app.route("/post/<post_id>/excluir", methods=["GET", "POST"])
@login_required
def excluir_post(post_id):

    post = Post.query.get(post_id)

    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
    
        flash("Post excluído com sucesso", "alert-danger container")
        return redirect(url_for("home"))
    
    else:
        flash("Você não pode excluir posts que não foram criados por você!", "alert-danger container")
        return redirect(url_for("home"))




    

