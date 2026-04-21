class HostDB:
    def __init__(self):
        self.hosts = {}

    def add_host(self, mac, switch, port, ip="Unknown"):
        self.hosts[mac] = {
            "switch": switch,
            "port": port,
            "ip": ip
        }

    def get_hosts(self):
        return self.hosts
