from rest_framework import status


class PasswordChangeService:
    def __init__(self, user_instance):
        self.user = user_instance

    def execute(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if self.user.check_password(old_password):
            self.user.set_password(new_password)
            self.user.save()
            return {'message': 'Password changed successfully.'}, status.HTTP_200_OK
        return {'error': 'Incorrect old password.'}, status.HTTP_400_BAD_REQUEST
