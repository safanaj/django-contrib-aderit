
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
from django.contrib.auth.models import User, check_password

from account.models import Account
from django.contrib.auth.tokens import default_token_generator

from django.contrib.aderit.access_account import _get_model_from_auth_profile_module

class TokenBackend(object):
    """
    Backend per l'autenticazione via token
    """

    supports_inactive_user = False

    def authenticate(self, token=None):
        if token is not None:
            try:
                model = _get_model_from_auth_profile_module()
                user =  model.objects.get(token=token).user
                if default_token_generator.check_token(user, token):
                    return user
            except model.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


