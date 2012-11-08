from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int
import random, string, time

TOKEN_DURATION_SECONDS = getattr(settings, 'ACCESS_ACCOUNT_TOKEN_DURATION_SECONDS', 3600*48)

def make_random_unexpirable_token(len_random_part=32):
    population = string.ascii_letters + string.digits
    return "".join(random.sample(population, len_random_part))

def make_random_expirable_token(len_random_part=32):
    random_part = make_random_unexpirable_token(len_random_part=len_random_part)
    prefix_part = int_to_base36(int(time.time()))
    return "%s-%s" % (prefix_part, random_part)

def random_token_is_expired(token):
    splitted = token.split('-', 1)
    splitted_len = len(splitted)
    if splitted_len == 1:
        ## no prefix for timestamp, unexpirable
        return False
    else: ## splitted_len is 2, check for exipration
        return (int(time.time()) - base36_to_int(splitted[0])) > TOKEN_DURATION_SECONDS

def check_random_token_is_valid(token):
    return not random_token_is_expired(token)

