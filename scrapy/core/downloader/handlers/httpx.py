import httpx
from twisted.internet.defer import ensureDeferred

from scrapy.http import HtmlResponse, JsonResponse, Response


class HTTPXDownloadHandler:
    def __init__(self, settings, crawler=None):
        self.settings = settings

    def download_request(self, request, spider):
        return ensureDeferred(self._download(request))

    async def _download(self, request):
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=str(request.url),
                headers=request.headers.to_unicode_dict(),
                content=request.body or None,
                timeout=10,
            )
            content_type = resp.headers.get("content-type", "").lower()
            response_cls = Response
            if "text/html" in content_type:
                response_cls = HtmlResponse
            elif "application/json" in content_type or "json" in content_type:
                response_cls = JsonResponse
            return response_cls(
                url=str(request.url),
                status=resp.status_code,
                headers=resp.headers,
                body=resp.content,
                request=request,
            )
