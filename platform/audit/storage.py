"""Audit Storage Backends for Azure"""
from typing import List, Optional
from .models import AuditRecord, AuditQuery
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InMemoryAuditStorage:
    def __init__(self):
        self._records: List[AuditRecord] = []
        self._lock = threading.Lock()
    
    def store(self, record: AuditRecord):
        with self._lock:
            self._records.append(record)
    
    def query(self, query: AuditQuery) -> List[AuditRecord]:
        with self._lock:
            return [r for r in self._records if self._matches_query(r, query)]
    
    def _matches_query(self, record: AuditRecord, query: AuditQuery) -> bool:
        if query.event_types and record.event_type not in query.event_types:
            return False
        if query.user_ids and record.user_id not in query.user_ids:
            return False
        if query.domains and record.domain not in query.domains:
            return False
        if query.start_time and record.timestamp < query.start_time:
            return False
        if query.end_time and record.timestamp > query.end_time:
            return False
        return True

class AzureBlobAuditStorage:
    def __init__(self, connection_string: str, container_name: str = "audit-logs"):
        self.connection_string = connection_string
        self.container_name = container_name
        self._client = None
        self._initialized = False
    
    def _initialize(self):
        if self._initialized:
            return
        try:
            from azure.storage.blob import BlobServiceClient
            self._client = BlobServiceClient.from_connection_string(self.connection_string)
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {e}")
    
    def store(self, record: AuditRecord):
        self._initialize()
        if not self._initialized:
            return
        
        try:
            # Create blob name with date and event ID
            date_str = record.timestamp.strftime("%Y/%m/%d")
            blob_name = f"{date_str}/{record.event_id}.json"
            
            blob_client = self._client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            # Upload the audit record as JSON
            blob_client.upload_blob(
                json.dumps(record.dict()),
                overwrite=True,
                content_type="application/json"
            )
        except Exception as e:
            logger.error(f"Failed to store audit record in Azure Blob: {e}")
    
    def query(self, query: AuditQuery) -> List[AuditRecord]:
        self._initialize()
        if not self._initialized:
            return []
        
        try:
            container_client = self._client.get_container_client(self.container_name)
            records = []
            
            # List blobs and filter by query
            blob_list = container_client.list_blobs()
            for blob in blob_list:
                if self._matches_blob_name(blob.name, query):
                    blob_client = container_client.get_blob_client(blob.name)
                    data = blob_client.download_blob().readall()
                    record = AuditRecord.parse_raw(data)
                    if self._matches_query(record, query):
                        records.append(record)
            
            return records
        except Exception as e:
            logger.error(f"Failed to query audit records from Azure Blob: {e}")
            return []
    
    def _matches_blob_name(self, blob_name: str, query: AuditQuery) -> bool:
        # Extract date from blob name (format: YYYY/MM/DD/event_id.json)
        if "/" not in blob_name:
            return True
        
        date_part = blob_name.split("/")[0]
        try:
            blob_date = datetime.strptime(date_part, "%Y/%m/%d")
            if query.start_time and blob_date < query.start_time:
                return False
            if query.end_time and blob_date > query.end_time:
                return False
        except:
            pass
        
        return True
    
    def _matches_query(self, record: AuditRecord, query: AuditQuery) -> bool:
        if query.event_types and record.event_type not in query.event_types:
            return False
        if query.user_ids and record.user_id not in query.user_ids:
            return False
        if query.domains and record.domain not in query.domains:
            return False
        if query.sensitivity_levels and record.sensitivity not in query.sensitivity_levels:
            return False
        return True
