import aiohttp
import asyncio
from typing import Optional, Dict, Any, Tuple
from django.conf import settings
import logging
from ..models import CustomUser

logger = logging.getLogger(__name__)

class AsyncOAuth42Service:
    def __init__(self):
        self.client_id = settings.OAUTH_42_CLIENT_ID
        self.client_secret = settings.OAUTH_42_CLIENT_SECRET
        self.redirect_uri = f"{settings.SITE_URL}/api/authentication/oauth/42/callback"
        self._session: Optional[aiohttp.ClientSession] = None
        # To avoid data race on simultaneous requests
        self._lock = asyncio.Lock()
        # Recurring requests to 42 API limited to 2
        self._semaphore = asyncio.Semaphore(2)


    ''' Context manager entry '''
    async def __aenter__(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self



    ''' Context manager exit '''
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None 



    async def _make_42_api_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                async with self._semaphore:
                    async with self._session.request(method, url, **kwargs) as response:
                        if response.status == 429: # Rate limit
                            retry_after = int(response.headers.get('Retry_After', 5))
                            logger.warning(f"Rate limit, wait {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        await response.raise_for_status()
                        return await response.json()
            
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(retry_delay * (attempt + 1))



    ''' Exchange code for access_token '''
    async def exchange_code_for_token(self, code: str) -> str:
        async with self._lock:
            return await self._make_42_api_request(
                'POST',
                'https://api.intra.42.fr/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'redirect_uri': self.redirect_uri
                }
            )
    


    async def get_user_data(self, access_token: str) -> Dict[str, Any]:
        return await self._make_42_api_request(
            'GET',
            'https://api.intra.42.fr/v2/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )



    async def get_or_create_user(self, user_data: Dict[str, Any]) -> Tuple[CustomUser, bool]:
        async with self._lock:
            user = await CustomUser.objects.filter(email=user_data['email']).afirst()

            if user:
                user.avatar_url = user_data['image']['link']
                await user.asave()
                return user, False
            else:
                user = await CustomUser.objects.acreate(
                    username=user_data['login'],
                    email=user_data['email'],
                    avatar_url=user_data['image']['link']
                )
                return user, True
    


''' Create instance of the service '''
async_oauth_42_service = AsyncOAuth42Service()