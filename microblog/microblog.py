from app import create_app, db, cli  # `import` first time would execute top-line sentences
from app.models import User, Post

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
