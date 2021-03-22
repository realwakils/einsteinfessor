from package import db
from package.models import User, Calcuation 
import geoip2.webservice

def IP():
    ip = User.query.first().ip
    with geoip2.webservice.Client(441963, 'bg1TFDhovW6vv6bL') as client:
        response = client.insights(ip)
        print(response.country.name)
        print(response.subdivisions.most_specific.name)
        print(response.city.name)