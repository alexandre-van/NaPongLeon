import aiohttp
import asyncio
from io import BytesIO
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
        self._lock = None
        self._session = None
        # Recurring requests to 42 API limited to 2
        self._semaphore = asyncio.Semaphore(2)



    ''' Context manager entry '''
    async def __aenter__(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        await self.__ensure_lock__()
        return self
    


    async def __ensure_lock__(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    


    ''' Context manager exit '''
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None 



    async def _ensure_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )



    async def _make_42_api_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        await self._ensure_session()
        
        if not self._session:
            raise RuntimeError("Failed to create session")

        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with self._semaphore:
                    async with self._session.request(method, url, **kwargs) as response:
                        if response.status == 429:  # Rate limit
                            retry_after = int(response.headers.get('Retry_After', 5))
                            logger.warning(f"Rate limit, wait {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"HTTP {response.status}: {error_text}")
                            
                        response.raise_for_status()
                        data = await response.json()
                        return data
            
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Final attempt failed: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(retry_delay * (attempt + 1))
    


    async def exchange_code_for_token(self, code: str) -> str:
        await self._ensure_session()

        async with self._lock:
            try:
                data = {
                    'grant_type': 'authorization_code',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'redirect_uri': self.redirect_uri
                }
                
                for key, value in data.items():
                    if key in ['code', 'client_id', 'client_secret']:
                        (f"{key}: {value[:10]}...")
                    else:
                        (f"{key}: {value}")

                return await self._make_42_api_request(
                    'POST',
                    'https://api.intra.42.fr/oauth/token',
                    data=data
                )
                    
                    
            except aiohttp.ClientError as e:
                logger.error(f"Request failed: {str(e)}")
                raise
    


    async def get_user_data(self, access_token_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            access_token = access_token_data.get('access_token')
            if not access_token:
                raise ValueError('No access token provided')
        
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }

            result = await self._make_42_api_request(
                'GET',
                'https://api.intra.42.fr/v2/me',
                headers=headers
            )
            if not result:
                raise ValueError('No data received from API')
            
            return result

        except aiohttp.ClientError as e:
            logger.error(f"Failed to get user data: {str(e)}")
            raise



    async def download_avatar(self, url:str) -> BytesIO:
        await self._ensure_session()

        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.read()
            return BytesIO(data)



    async def get_or_create_user(self, user_data: Dict[str, Any]) -> CustomUser:
        from django.core.files.storage import default_storage
        from ..utils.image_process import process_image
        from asgiref.sync import sync_to_async
        from django.contrib.auth.hashers import make_password
        import uuid

        async with self._lock:
            new_username = user_data['login'] + '_42'
            user = await CustomUser.objects.filter(username=new_username).afirst()

            if user:
                (f"existing user: {user}")
            else:
                user = await CustomUser.objects.acreate(
                    username=new_username,
                    password=make_password(uuid.uuid4().hex),
                    email=user_data['email']
                )

                if avatar_url := user_data.get('image', {}).get('link'):
                    avatar_content = await self.download_avatar(avatar_url)
                    filename = f"avatar_{user.id}.jpg"
                    filepath = f"users/{user.id}/avatar/{filename}"
                    new_path = await sync_to_async(default_storage.save)(filepath, avatar_content)
                    await user.update_avatar_url(new_path)

            return user
    


''' Create instance of the service '''
async_oauth_42_service = AsyncOAuth42Service()