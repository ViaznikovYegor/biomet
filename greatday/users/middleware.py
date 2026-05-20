import requests
from django.utils.deprecation import MiddlewareMixin


class GeoLocationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Получаем реальный IP пользователя
        ip = self.get_client_ip(request)

        # Если это локальный адрес (разработка), задаём тестовые координаты
        if ip in ('127.0.0.1', 'localhost', '::1'):
            request.client_ip = {
                'status': 'success',
                'lat': 25.77,
                'lon': 80.20,
                'city': 'Краснодар',
                'country': 'Россия',
            }
            return None

        # Пытаемся определить геолокацию через ip-api.com
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
            data = response.json()
            if data.get('status') == 'success':
                request.client_ip = data
            else:
                # Если не удалось, сохраняем только IP
                request.client_ip = {'status': 'fail', 'client_ip': ip}
        except requests.RequestException:
            request.client_ip = {'status': 'error', 'client_ip': ip}

        return None

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip