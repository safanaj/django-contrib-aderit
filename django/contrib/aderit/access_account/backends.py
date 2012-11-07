
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django.conf import settings
from django.utils.log import getLogger
from django.contrib.auth.models import User, check_password
from django.contrib.auth.tokens import default_token_generator

from django.contrib.aderit.access_account import _get_model_from_auth_profile_module

logger = getLogger('aderit.access_account.auth_backend')

class TokenBackend(object):
    """
    Backend per l'autenticazione via token
    """

    supports_inactive_user = False

    def authenticate(self, token=None, user=None):
        """
        Se non posso cercare il @token nel DB (il modello non ha il campo token) ed ho @user
        provo default_token_generator.check_token

        Se posso cercarlo sul DB:
          1 - lo trovo:
              + @user passato deve corrispondere al @token trovato sul DB
          2 - non lo trovo:
              + provo usando default_token_generator.check_token

        Se @user e' passato ma non ha l'attributo last_login (usato nel chek_token), non autentico.
        """
        logger.debug("authenticate ( token=%s , user=%s )", token, user)
        if token is not None:
            model = _get_model_from_auth_profile_module()
            if hasattr(model, 'token'):
                try:
                    user_profile =  model.objects.get(token=token)
                    if user is None:
                        return user_profile.user
                    elif user == user_profile.user:
                        return user
                except model.DoesNotExist:
                    try:
                        if user is not None and default_token_generator.check_token(user, token):
                            logger.debug("token DoenNotExist but (user: %s , token: %s) is valid, auth OK",
                                         user, token)
                            return user
                    except AttributeError, e:
                        logger.error("user[%s] can not be authenticate: %s", user, e)
                        pass
            else:
                try:
                    if user is not None and default_token_generator.check_token(user, token):
                        logger.debug("model[%s] have not token field (user: %s , token: %s) is valid, auth OK",
                                     model, user, token)
                        return user
                except AttributeError:
                    logger.error("user[%s] can not be authenticate: %s", user, e)
                    pass
        logger.debug("authenticate ( token=%s , user=%s ), fail", token, user)
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


