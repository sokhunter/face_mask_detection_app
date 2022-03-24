import re

from accounts.models import UserPasswordHistory
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class HasUpperCaseValidator:
    def validate(self, password, user=None):
        if re.search('[A-Z]', password) is None:
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter en mayúscula."),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return _("Su contraseña debe contener al menos un carácter en mayúscula.")


class HasNumberValidator:
    def validate(self, password, user=None):
        if re.search('[0-9]', password) is None:
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter numérico."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("Su contraseña debe contener al menos un carácter numérico.")


class DontRepeatValidator:
    def __init__(self, history=3):
        self.history = history

    def validate(self, password, user=None):
        for old_pass in self._get_last_passwords(user):
            if check_password(password=password, encoded=old_pass):
                self._raise_validation_error()
            else:
                self._delete_oldest_password(user)

    def get_help_text(self):
        return _("La contraseña debe de ser distinta a las últimas ${self.history}")

    def _raise_validation_error(self):
        raise ValidationError(
            _("Su contraseña debe de ser distinta a las últimas %(history)s."),
            code='password_has_been_used',
            params={'history': self.history}
        )

    def _get_last_passwords(self, user):
        all_history_user_passwords = UserPasswordHistory.objects.filter(
            user=user).order_by('id')
        return [p.password for p in all_history_user_passwords]

    def _delete_oldest_password(self, user):
        all_history_user_passwords = UserPasswordHistory.objects.filter(
            user=user).order_by('id')
        if all_history_user_passwords.count() == self.history:
            password_to_delete = all_history_user_passwords.count() - self.history + 1
            for i in all_history_user_passwords[:password_to_delete][::-1]:
                i.delete()
