import httpx
from typing import Optional, Dict
from loguru import logger


class LinkedInClient:
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url
        self._api_key = api_key
        self.api_key_truncated = api_key[:15] + "..." if len(api_key) > 15 else "***"
        logger.info(f"LinkedIn client initialized. Base URL: {base_url}, Key: {self.api_key_truncated}")
    
    async def enrich_lead(self, name: str, company: str) -> Dict[str, Optional[str]]:
        """
        Enrich lead data using LinkedIn API (or alternative enrichment service).
        
        Args:
            name: Lead's full name
            company: Company name
        
        Returns:
            Dict with enrichment data: {
                "linkedin_role": str | None,
                "linkedin_company_size": str | None,
                "linkedin_location": str | None,
                "linkedin_industry": str | None
            }
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/people/enrich",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    params={
                        "name": name,
                        "company": company
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                
                enriched = {
                    "linkedin_role": data.get("title") or data.get("role"),
                    "linkedin_company_size": data.get("company_size"),
                    "linkedin_location": data.get("location"),
                    "linkedin_industry": data.get("industry")
                }
                
                logger.info(f"LinkedIn enrichment successful for: {name[:20]}...")
                return enriched
                
        except httpx.HTTPStatusError as e:
            error_msg = str(e)[:200]
            logger.warning(f"LinkedIn enrichment HTTP error: {error_msg}")
            return {
                "linkedin_role": None,
                "linkedin_company_size": None,
                "linkedin_location": None,
                "linkedin_industry": None
            }
        except Exception as e:
            error_msg = str(e)[:200]
            logger.warning(f"LinkedIn enrichment failed: {error_msg}")
            return {
                "linkedin_role": None,
                "linkedin_company_size": None,
                "linkedin_location": None,
                "linkedin_industry": None
            }
