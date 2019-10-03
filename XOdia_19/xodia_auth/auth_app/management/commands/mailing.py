from django.core.mail import send_mail
from auth_app.models import Profile
from django.core.management import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Sends mail to everyone in the database"

    def handle(self, *args, **kwargs):
        receivers = []
        for user in User.objects.all():
            receivers.append(user.email)
        send_mail("Bot Submissions have begun!", "Greetings from XOdia!\n\nWe are delighted to announce that bot submissions will now be accepted on our website, www.xodia.in.\nTest your bots against other bots and see where you stand on the leaderboard!\nThe last date for bot submissions is 26 October, 2019.\n\nAlso, please note the following changes in the documentation:\n1. The first bot will be given initial input 0 and the second bot will be given initial input 1 (section 1.2).\n2. Response time for the bot has been increased from 2 seconds to 3 seconds (section 3).\n\n With best regards,\nTeam XOdia", 'credenz.xodia19@gmail.com', receivers)
        print("Mail Sent")
