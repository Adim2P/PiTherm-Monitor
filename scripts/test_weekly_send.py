import src.pitherm.logging_service as test
from datetime import datetime

test._TEST_MODE = True

fake_now = datetime(2026, 4, 19, 8, 0)

test.check_and_send_monthly_report(fake_now)