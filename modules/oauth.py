from authlib.integrations.django_client import OAuth

oauth = OAuth()
oauth.register(name='concat-test')
oauth.register(name='concat-prod')