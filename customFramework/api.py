import logging
from typing import Optional

from parse import parse
from webob import Request, Response

from customFramework import exceptions

logger = logging.getLogger(__name__)


class API:
    _routes = {}

    def __call__(self, environ, start_response) -> Response:
        request = Request(environ=environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def _get_route_handler(self, route) -> tuple[Optional[callable], Optional[str]]:
        for path, handler in self._routes.items():
            parse_result = parse(path, route)
            if parse_result is not None:
                return handler, parse_result.named

        return None, None

    @staticmethod
    def get_404_response() -> Response:
        response = Response()
        response.text = 'Route not found'
        response.status = 404
        return response

    def handle_request(self, request) -> Response:

        handler, kwargs = self._get_route_handler(request.path)
        if handler:
            response: Response = handler(request, **kwargs)
        else:
            response = self.get_404_response()

        logger.info(f'{request.method} {response.status} response for {request.path} route')
        return response

    def route(self, path):
        """Register route"""
        if path in self._routes:
            raise exceptions.DuplicateRoute("Such route already exists.")

        def wrapper(route_handler: callable, *args, **kwargs):
            self._routes[path] = route_handler
            return route_handler

        return wrapper