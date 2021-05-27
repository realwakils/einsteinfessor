from package import app
from package.models import User
from package import db

prod = app.config['ENV'] == 'production'

def getUserIP(request):
    return request.headers['X-Forwarded-For'].split(',')[0] if prod else request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    
def submitLocationToDatabase(user_ip, location):
    user = User.query.get(user_ip)
    user.latest_url_visited = location
    db.session.commit()