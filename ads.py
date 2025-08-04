import httpx
import random
from config import (
    ADS_ENABLED, ADS_FREQUENCY, ADS_PLACEMENT, ADS_TYPE
)

class AdsManager:
    def __init__(self):
        self.ad_stats = {
            'total_ads_shown': 0,
            'adsgram_ads': 0,
            'fallback_ads': 0,
            'errors': 0
        }
        # AdsGram Configuration
        self.ADSGRAM_BLOCK_ID = 13419  # Your AdsGram block ID
        self.ADSGRAM_API_URL = "https://api.adsgram.ai/advbot"
    
    async def get_ad(self, user_id: int, language: str = "en") -> dict:
        """Get an ad from AdsGram or fallback"""
        if not ADS_ENABLED:
            return None
        
        try:
            # Try to get ad from AdsGram
            ad_content = await self._fetch_adsgram_ad(user_id, language)
            if ad_content:
                self.ad_stats['adsgram_ads'] += 1
                self.ad_stats['total_ads_shown'] += 1
                return ad_content
            
            # No fallback ads - only show AdsGram ads
            print("🔗 No AdsGram ads available, not showing any ads")
            return None
            
        except Exception as e:
            print(f"Error getting ad: {e}")
            self.ad_stats['errors'] += 1
            return None
    
    async def _fetch_adsgram_ad(self, user_id: int, language: str = "en") -> dict:
        """Fetch ad from AdsGram API using new format"""
        try:
            # Construct AdsGram API request with new format
            params = {
                'tgid': user_id,
                'blockid': self.ADSGRAM_BLOCK_ID,
                'language': language
            }
            
            print(f"🔗 Fetching AdsGram ad for user {user_id}")
            print(f"🔗 API URL: {self.ADSGRAM_API_URL}")
            print(f"🔗 Block ID: {self.ADSGRAM_BLOCK_ID}")
            print(f"🔗 Language: {language}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ADSGRAM_API_URL, params=params, timeout=10)
            
            print(f"🔗 Response status: {response.status_code}")
            print(f"🔗 Response text: {response.text}")
            
            if response.status_code == 200:
                # Check if response contains "No available advertisement"
                if "No available advertisement" in response.text:
                    print(f"🔗 No ads available from AdsGram: {response.text}")
                    return None
                
                # Check if response is empty
                if not response.text.strip():
                    print(f"🔗 Empty response from AdsGram")
                    return None
                
                try:
                    data = response.json()
                    print(f"🔗 Response data: {data}")
                    
                    # Check if we have valid ad data with required fields
                    if data and isinstance(data, dict):
                        # Check for required fields that indicate a real ad
                        if 'text_html' in data or 'click_url' in data or 'button_name' in data:
                            print(f"🔗 Valid AdsGram ad found!")
                            return data
                        else:
                            print(f"🔗 Invalid ad data structure: {data}")
                            return None
                    else:
                        print(f"🔗 No valid ad data in response: {data}")
                        return None
                except Exception as json_error:
                    print(f"🔗 Error parsing JSON response: {json_error}")
                    print(f"🔗 Raw response: {response.text}")
                    return None
            else:
                print(f"🔗 API error: {response.status_code} - {response.text}")
                return None
            
        except httpx.RequestError as e:
            print(f"🔗 Network error fetching AdsGram ad: {e}")
            return None
        except Exception as e:
            print(f"🔗 Error fetching AdsGram ad: {e}")
            return None
    
    def _get_fallback_ad(self, language: str) -> dict:
        """No fallback ads - only show real AdsGram ads"""
        return None
    
    def should_show_ad(self, user_id: int) -> bool:
        """Check if ad should be shown based on frequency"""
        # Show ad after every reminder (ADS_FREQUENCY = 1)
        return ADS_ENABLED and ADS_FREQUENCY > 0
    
    def get_ad_stats(self) -> dict:
        """Get advertising statistics"""
        return self.ad_stats.copy()
    
    def reset_stats(self):
        """Reset advertising statistics"""
        self.ad_stats = {
            'total_ads_shown': 0,
            'adsgram_ads': 0,
            'fallback_ads': 0,
            'errors': 0
        } 