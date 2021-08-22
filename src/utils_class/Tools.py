import requests

class IP_Tools:
    def __init__(self):
        pass

    def ip_lookup(self, ip: str):
        # businessName, businessWebsite, city, continent, country, countryCode, ipName, ipType, isp, lat, lon, org, query, region, status
        return requests.get(f'https://extreme-ip-lookup.com/json/{ip}').json()