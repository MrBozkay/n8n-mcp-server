"""
n8n API Client

n8n Cloud instance'ıyla güvenli ve verimli iletişim kurmak için HTTP client sınıfı.
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
import structlog
from pydantic import BaseModel, Field


logger = structlog.get_logger(__name__)


class WorkflowModel(BaseModel):
    """n8n Workflow modeli"""
    id: Optional[str] = None
    name: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    connections: Dict[str, Any] = Field(default_factory=dict)
    active: bool = False
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    staticData: Optional[Dict[str, Any]] = None
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    pinData: Optional[Dict[str, Any]] = Field(default_factory=dict)
    versionId: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class N8nApiError(Exception):
    """n8n API ile ilgili hatalar için özel exception"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class N8nApiClient:
    """
    n8n Cloud API Client
    
    n8n workflow'larını yönetmek için HTTP client sınıfı.
    Hata yönetimi, retry mekanizması ve performans optimizasyonu içerir.
    """
    
    def __init__(
        self, 
        base_url: str, 
        api_key: str, 
        timeout: int = 30,
        max_retries: int = 3,
        cache_ttl: int = 300
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        
        # Cache için basit memory storage
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # HTTP client yapılandırması
        self.client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api/v1",
            headers={
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=self.timeout,
        )
        
        logger.info("n8n API Client initialized", base_url=self.base_url)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def close(self):
        """HTTP client'ı kapat"""
        await self.client.aclose()
        logger.info("n8n API Client closed")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Cache'in geçerli olup olmadığını kontrol et"""
        if cache_key not in self._cache:
            return False
        
        cached_at = self._cache[cache_key].get("cached_at")
        if not cached_at:
            return False
        
        return datetime.now() - cached_at < timedelta(seconds=self.cache_ttl)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Cache'den veri al"""
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key].get("data")
        return None
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]):
        """Cache'e veri kaydet"""
        self._cache[cache_key] = {
            "data": data,
            "cached_at": datetime.now()
        }
    
    def _clear_cache(self):
        """Cache'i temizle"""
        self._cache.clear()
        logger.debug("Cache cleared")
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = False
    ) -> Dict[str, Any]:
        """
        HTTP isteği yap, retry mekanizması ve hata yönetimi ile
        """
        cache_key = f"{method}:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        
        # Cache kontrolü (sadece GET istekleri için)
        if method.upper() == "GET" and use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.debug("Cache hit", endpoint=endpoint)
                return cached_data
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    "Making HTTP request", 
                    method=method, 
                    endpoint=endpoint, 
                    attempt=attempt + 1
                )
                
                response = await self.client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    params=params
                )
                
                # HTTP hata kodları kontrolü
                if response.status_code >= 400:
                    error_data = None
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text}
                    
                    error_msg = f"n8n API error: {response.status_code}"
                    if error_data and "message" in error_data:
                        error_msg += f" - {error_data['message']}"
                    
                    raise N8nApiError(
                        error_msg, 
                        response.status_code, 
                        error_data
                    )
                
                # Başarılı yanıt
                result = response.json()
                
                # Cache'e kaydet (sadece GET istekleri için)
                if method.upper() == "GET" and use_cache:
                    self._set_cache(cache_key, result)
                
                logger.info(
                    "HTTP request successful", 
                    method=method, 
                    endpoint=endpoint,
                    status_code=response.status_code
                )
                
                return result
                
            except httpx.TimeoutException as e:
                last_exception = N8nApiError(f"Request timeout: {str(e)}")
                logger.warning("Request timeout", attempt=attempt + 1, endpoint=endpoint)
                
            except httpx.NetworkError as e:
                last_exception = N8nApiError(f"Network error: {str(e)}")
                logger.warning("Network error", attempt=attempt + 1, endpoint=endpoint)
                
            except N8nApiError:
                # API hatalarını direkt fırlat, retry yapma
                raise
                
            except Exception as e:
                last_exception = N8nApiError(f"Unexpected error: {str(e)}")
                logger.error("Unexpected error", attempt=attempt + 1, error=str(e))
            
            # Son deneme değilse bekle
            if attempt < self.max_retries:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info("Retrying request", wait_time=wait_time)
                await asyncio.sleep(wait_time)
        
        # Tüm denemeler başarısız oldu
        raise last_exception or N8nApiError("Max retries exceeded")
    
    async def health_check(self) -> bool:
        """API sağlığını kontrol et"""
        try:
            await self._make_request("GET", "/workflows", params={"limit": 1})
            logger.info("Health check passed")
            return True
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return False
    
    # ======================== WORKFLOW CRUD OPERASYONLARI ========================
    
    async def create_workflow(self, workflow: WorkflowModel) -> WorkflowModel:
        """Yeni workflow oluştur"""
        workflow_data = workflow.model_dump(exclude_unset=True, exclude_none=True)
        
        logger.info("Creating workflow", name=workflow.name)
        
        result = await self._make_request("POST", "/workflows", data=workflow_data)
        
        # Cache'i temizle çünkü yeni workflow eklendi
        self._clear_cache()
        
        logger.info("Workflow created successfully", id=result.get("id"), name=workflow.name)
        
        return WorkflowModel(**result)
    
    async def get_workflow(self, workflow_id: str, use_cache: bool = True) -> Optional[WorkflowModel]:
        """Workflow ID'sine göre workflow getir"""
        logger.info("Getting workflow", id=workflow_id)
        
        try:
            result = await self._make_request(
                "GET", 
                f"/workflows/{workflow_id}", 
                use_cache=use_cache
            )
            logger.info("Workflow retrieved successfully", id=workflow_id)
            return WorkflowModel(**result)
            
        except N8nApiError as e:
            if e.status_code == 404:
                logger.warning("Workflow not found", id=workflow_id)
                return None
            raise
    
    async def update_workflow(self, workflow_id: str, workflow: WorkflowModel) -> WorkflowModel:
        """Workflow'u güncelle"""
        workflow_data = workflow.model_dump(exclude_unset=True, exclude_none=True)
        
        logger.info("Updating workflow", id=workflow_id, name=workflow.name)
        
        result = await self._make_request(
            "PUT", 
            f"/workflows/{workflow_id}", 
            data=workflow_data
        )
        
        # Cache'i temizle çünkü workflow güncellendi
        self._clear_cache()
        
        logger.info("Workflow updated successfully", id=workflow_id)
        
        return WorkflowModel(**result)
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Workflow'u sil"""
        logger.info("Deleting workflow", id=workflow_id)
        
        try:
            await self._make_request("DELETE", f"/workflows/{workflow_id}")
            
            # Cache'i temizle çünkü workflow silindi
            self._clear_cache()
            
            logger.info("Workflow deleted successfully", id=workflow_id)
            return True
            
        except N8nApiError as e:
            if e.status_code == 404:
                logger.warning("Workflow not found for deletion", id=workflow_id)
                return False
            raise
    
    async def list_workflows(
        self, 
        active: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        use_cache: bool = True
    ) -> List[WorkflowModel]:
        """Workflow'ları listele"""
        params = {
            "limit": limit
        }
        
        if active is not None:
            params["active"] = active
            
        if tags:
            params["tags"] = ",".join(tags)
        
        logger.info("Listing workflows", params=params)
        
        result = await self._make_request(
            "GET", 
            "/workflows", 
            params=params,
            use_cache=use_cache
        )
        
        workflows = []
        for workflow_data in result.get("data", []):
            workflows.append(WorkflowModel(**workflow_data))
        
        logger.info("Workflows listed successfully", count=len(workflows))
        
        return workflows
    
    async def search_workflows(self, query: str, limit: int = 20) -> List[WorkflowModel]:
        """Workflow'ları isme göre ara"""
        logger.info("Searching workflows", query=query, limit=limit)
        
        # n8n API'si doğrudan arama desteklemiyorsa, tüm workflow'ları getir ve filtrele
        all_workflows = await self.list_workflows(limit=100)  # Daha büyük limit
        
        # Basit text matching (case-insensitive)
        matched_workflows = []
        query_lower = query.lower()
        
        for workflow in all_workflows:
            if (query_lower in workflow.name.lower() or 
                any(query_lower in tag.get("name", "").lower() for tag in workflow.tags)):
                matched_workflows.append(workflow)
                
                if len(matched_workflows) >= limit:
                    break
        
        logger.info("Workflow search completed", query=query, found=len(matched_workflows))
        
        return matched_workflows
    
    async def activate_workflow(self, workflow_id: str) -> bool:
        """Workflow'u aktif et"""
        logger.info("Activating workflow", id=workflow_id)
        
        try:
            await self._make_request("POST", f"/workflows/{workflow_id}/activate")
            self._clear_cache()
            logger.info("Workflow activated successfully", id=workflow_id)
            return True
        except N8nApiError as e:
            if e.status_code == 404:
                logger.warning("Workflow not found for activation", id=workflow_id)
                return False
            raise
    
    async def deactivate_workflow(self, workflow_id: str) -> bool:
        """Workflow'u pasif et"""
        logger.info("Deactivating workflow", id=workflow_id)
        
        try:
            await self._make_request("POST", f"/workflows/{workflow_id}/deactivate")
            self._clear_cache()
            logger.info("Workflow deactivated successfully", id=workflow_id)
            return True
        except N8nApiError as e:
            if e.status_code == 404:
                logger.warning("Workflow not found for deactivation", id=workflow_id)
                return False
            raise
    
    async def execute_workflow(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Workflow'u manuel çalıştır"""
        logger.info("Executing workflow", id=workflow_id)
        
        execution_data = {"workflowData": {"id": workflow_id}}
        if input_data:
            execution_data["input"] = input_data
        
        result = await self._make_request("POST", "/executions", data=execution_data)
        
        logger.info("Workflow execution started", id=workflow_id, execution_id=result.get("id"))
        
        return result