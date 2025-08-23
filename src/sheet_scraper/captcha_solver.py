from twocaptcha.solver import TwoCaptcha

class CaptchaSolver:
    def __init__(self, api_key):
        self.solver = TwoCaptcha(api_key)

    def solve_recaptcha(self, sitekey, url):
        try:
            result = self.solver.recaptcha(
                sitekey=sitekey,
                url=url
            )
            return result['code']
        except Exception as e:
            print(f"Error solving CAPTCHA: {e}")
            return None
