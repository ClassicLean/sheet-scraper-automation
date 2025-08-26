class ProxyManager:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_proxy_index = 0

    def get_proxy(self):
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
