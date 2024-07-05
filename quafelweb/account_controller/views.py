from typing import Callable, Optional
from django.http import HttpRequest, HttpResponse
from authlib.integrations.django_client import OAuth
from django.shortcuts import redirect, render
from django.urls import reverse
from quafelweb.settings import OPENID_CONF_URL, OPENID_SECRET, OPENID_CLIENT_ID, OPENID_CLIENT_IDENT

OAUTH = OAuth()
OAUTH.register(
  name='openid',
  server_metadata_url=OPENID_CONF_URL,
  client_id = OPENID_CLIENT_ID,
  client_secret = OPENID_SECRET,
  client_kwargs={'scope': 'openid email'}
)


class AccountView:

  ACCOUNTS = ['ulqho@student.kit.edu' ] * 300
  
  @staticmethod
  def require_login(view : Callable) -> HttpResponse:

    def _decorator(request : HttpResponse):
      if AccountView.is_logged_in(request):
        return view(request)
      return AccountView.authenticate(request) 

    return _decorator
  

  @staticmethod
  @require_login
  def manage_accounts(request : HttpRequest) -> HttpResponse:
    return render(request, "account.html", context={"accounts" : AccountView.ACCOUNTS})


  @staticmethod
  def add_admin(request) -> HttpResponse:
    ...

  @staticmethod
  def remove_admin(request) -> HttpResponse:
    ...
  
  @staticmethod
  def search(request) -> HttpResponse:
    ...

  @staticmethod
  def authenticate(request : HttpRequest) -> HttpResponse:
    if AccountView.is_logged_in(request):
      redirect_url =  request.build_absolute_uri() 
      if redirect_url == request.build_absolute_uri(reverse('login')):
        return redirect('/')
    request.session["last_request"] = request.build_absolute_uri()
    return OAUTH.openid.authorize_redirect(request, request.build_absolute_uri(reverse('auth_callback')))


  @staticmethod
  def authenticate_callback(request : HttpRequest) -> HttpResponse:
    token = OAUTH.openid.authorize_access_token(request)

    if not token["userinfo"][OPENID_CLIENT_IDENT] in AccountView.ACCOUNTS: # TODO replace this with an data base access
      return redirect(reverse('denied'))

    request.session['admin_ident'] = token['userinfo'][OPENID_CLIENT_IDENT]
    request.session['logged_in'] = True
    return redirect(request.session.get("last_request", '/'))
  
  @staticmethod
  def get_identifier(request : HttpRequest) -> Optional[str]:
    if not AccountView.is_logged_in(request): return None
    return request.session.get('admin_ident')

  @staticmethod
  def is_logged_in(request : HttpRequest) -> bool:
    return 'admin_ident' in request.session
  
  @staticmethod
  def denied(request : HttpRequest):
    context = {
      'info_type' : 'error',
      'header' : 'No Access',
      'message' : 'You dont have access to this resource'
    }
    return render(request, 'info.html', context=context)
  
  @staticmethod
  def logout(request : HttpRequest):
    del request.session['admin_ident']
    del request.session['logged_in']

    return redirect('/')