"""
n8n MCP Server

n8n workflow'larını programatik olarak yönetmek için MCP (Model Context Protocol) 
standardını kullananan ana sunucu sınıfı.
"""

import asyncio
import os
import json
import sys
import logging
from typing import Optional
import structlog
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp import types

from .client import N8nApiClient
from .config import Settings, load_settings
from .logging_config import setup_logging


logger = structlog.get_logger(__name__)


def get_tool_definitions() -> list[types.Tool]:
    """Returns the static list of n8n tool definitions."""
    return [
        types.Tool(
            name="create_workflow",
            description="Create a new n8n workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the workflow"
                    },
                    "nodes": {
                        "type": "array",
                        "description": "Workflow nodes configuration",
                        "items": {"type": "object"},
                        "default": []
                    },
                    "connections": {
                        "type": "object",
                        "description": "Node connections configuration",
                        "default": {}
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Whether the workflow should be active",
                        "default": False
                    },
                    "tags": {
                        "type": "array",
                        "description": "Workflow tags",
                        "items": {"type": "object"},
                        "default": []
                    }
                },
                "required": ["name"]
            }
        ),
        
        types.Tool(
            name="get_workflow",
            description="Get a specific workflow by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID of the workflow to retrieve"
                    },
                    "use_cache": {
                        "type": "boolean",
                        "description": "Whether to use cached data",
                        "default": True
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        
        types.Tool(
            name="list_workflows",
            description="List workflows with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "active": {
                        "type": "boolean",
                        "description": "Filter by active status (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "description": "Filter by tags (optional)",
                        "items": {"type": "string"}
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of workflows to return",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of workflows to skip",
                        "default": 0,
                        "minimum": 0
                    }
                }
            }
        ),
        
        types.Tool(
            name="search_workflows",
            description="Search workflows by name or tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches in name and tags)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["query"]
            }
        ),
        
        types.Tool(
            name="update_workflow",
            description="Update an existing workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID of the workflow to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the workflow (optional)"
                    },
                    "nodes": {
                        "type": "array",
                        "description": "Updated nodes configuration (optional)",
                        "items": {"type": "object"}
                    },
                    "connections": {
                        "type": "object",
                        "description": "Updated connections configuration (optional)"
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Whether the workflow should be active (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "description": "Updated tags (optional)",
                        "items": {"type": "object"}
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        
        types.Tool(
            name="delete_workflow",
            description="Delete a workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID of the workflow to delete"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        
        types.Tool(
            name="activate_workflow",
            description="Activate a workflow to make it run automatically",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID of the workflow to activate"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        
        types.Tool(
            name="deactivate_workflow",
            description="Deactivate a workflow to stop it from running automatically",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID of the workflow to deactivate"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        
        types.Tool(
            name="health_check",
            description="Check n8n API connection health",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


class N8nMcpServer:
    """n8n MCP Server ana sınıfı"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.n8n_client: Optional[N8nApiClient] = None
        self.server = Server(self.settings.mcp.server_name)
        
        logger.info(
            "n8n MCP Server initialized", 
            server_name=self.settings.mcp.server_name,
            version=self.settings.mcp.version
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Sunucuyu başlat"""
        logger.info("Initializing n8n MCP Server...")
        
        # n8n API client'ı başlat
        self.n8n_client = N8nApiClient(
            base_url=self.settings.n8n.base_url,
            api_key=self.settings.n8n.api_key,
            timeout=self.settings.n8n.timeout,
            max_retries=self.settings.n8n.max_retries,
            cache_ttl=self.settings.performance.cache_ttl
        )
        
        # MCP handlers'ları kaydet
        await self._register_handlers()
        
        # Sağlık kontrolü yap
        try:
            is_healthy = await self.n8n_client.health_check()
            if not is_healthy:
                logger.warning("n8n API health check failed, but continuing...")
            else:
                logger.info("n8n API connection verified")
        except Exception as e:
            logger.warning("n8n API health check error", error=str(e))
        
        logger.info("n8n MCP Server initialization completed")
    
    async def cleanup(self):
        """Temizleme işlemleri"""
        logger.info("Cleaning up n8n MCP Server...")
        
        if self.n8n_client:
            await self.n8n_client.close()
        
        logger.info("n8n MCP Server cleanup completed")
    
    def _get_tool_handlers(self):
        """Returns a mapping of tool names to their handler methods."""
        return {
            "create_workflow": self._handle_create_workflow,
            "get_workflow": self._handle_get_workflow,
            "list_workflows": self._handle_list_workflows,
            "search_workflows": self._handle_search_workflows,
            "update_workflow": self._handle_update_workflow,
            "delete_workflow": self._handle_delete_workflow,
            "activate_workflow": self._handle_activate_workflow,
            "deactivate_workflow": self._handle_deactivate_workflow,
            "health_check": self._handle_health_check,
        }

    async def _register_handlers(self):
        """MCP handler'ları kaydet"""
        logger.info("Registering MCP handlers...")
        
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """Mevcut tool'ları listele"""
            logger.debug("Listing available tools")
            return get_tool_definitions()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
            """Tool çağrılarını işle"""
            logger.info(f"Tool called: {name}", arguments=arguments)
            
            handlers = self._get_tool_handlers()
            handler = handlers.get(name)

            try:
                if handler:
                    return await handler(arguments or {})
                else:
                    logger.warning(f"Unknown tool called: {name}")
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error("Tool execution error", tool_name=name, error=str(e))
                return [types.TextContent(
                    type="text",
                    text=f"Tool execution error: {str(e)}"
                )]
    
    # Tool Handler Methods
    async def _handle_create_workflow(self, args: dict) -> list[types.TextContent]:
        """Workflow oluşturma handler'ı"""
        if "name" not in args:
            return [types.TextContent(type="text", text="Missing required field: name")]
        
        try:
            from .client import WorkflowModel
            
            workflow = WorkflowModel(
                name=args["name"],
                nodes=args.get("nodes", []),
                connections=args.get("connections", {}),
                active=args.get("active", False),
                tags=args.get("tags", [])
            )
            
            created_workflow = await self.n8n_client.create_workflow(workflow)
            
            result = {
                "success": True,
                "message": f"Workflow '{created_workflow.name}' created successfully",
                "workflow": {
                    "id": created_workflow.id,
                    "name": created_workflow.name,
                    "active": created_workflow.active,
                    "nodes_count": len(created_workflow.nodes)
                }
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating workflow: {str(e)}")]
    
    async def _handle_get_workflow(self, args: dict) -> list[types.TextContent]:
        if "workflow_id" not in args:
            return [types.TextContent(type="text", text="Missing required field: workflow_id")]
        
        try:
            workflow = await self.n8n_client.get_workflow(
                args["workflow_id"], 
                use_cache=args.get("use_cache", True)
            )
            
            if workflow is None:
                return [types.TextContent(type="text", text=f"Workflow not found: {args['workflow_id']}")]
            
            result = {
                "success": True,
                "workflow": workflow.model_dump(mode="json")
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error getting workflow: {str(e)}")]
    
    async def _handle_list_workflows(self, args: dict) -> list[types.TextContent]:
        """Workflow listeleme handler'ı"""
        try:
            workflows = await self.n8n_client.list_workflows(
                active=args.get("active"),
                tags=args.get("tags"),
                limit=args.get("limit", 20),
                use_cache=True
            )
            
            workflow_list = []
            for workflow in workflows:
                workflow_list.append({
                    "id": workflow.id,
                    "name": workflow.name,
                    "active": workflow.active,
                    "nodes_count": len(workflow.nodes)
                })
            
            result = {
                "success": True,
                "count": len(workflow_list),
                "workflows": workflow_list
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing workflows: {str(e)}")]
    
    async def _handle_search_workflows(self, args: dict) -> list[types.TextContent]:
        """Workflow arama handler'ı"""
        if "query" not in args:
            return [types.TextContent(type="text", text="Missing required field: query")]
        
        try:
            workflows = await self.n8n_client.search_workflows(
                query=args["query"],
                limit=args.get("limit", 20)
            )
            
            workflow_list = []
            for workflow in workflows:
                workflow_list.append({
                    "id": workflow.id,
                    "name": workflow.name,
                    "active": workflow.active,
                    "nodes_count": len(workflow.nodes)
                })
            
            result = {
                "success": True,
                "query": args["query"],
                "found": len(workflow_list),
                "workflows": workflow_list
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error searching workflows: {str(e)}")]
    
    async def _handle_update_workflow(self, args: dict) -> list[types.TextContent]:
        """Workflow güncelleme handler'ı"""
        if "workflow_id" not in args:
            return [types.TextContent(type="text", text="Missing required field: workflow_id")]
        
        try:
            # Önce mevcut workflow'u getir
            existing_workflow = await self.n8n_client.get_workflow(args["workflow_id"])
            
            if existing_workflow is None:
                return [types.TextContent(type="text", text=f"Workflow not found: {args['workflow_id']}")]
            
            # Güncelleme verilerini hazırla - sadece sağlanan alanları güncelle
            from .client import WorkflowModel
            
            update_data = {
                "name": args.get("name", existing_workflow.name),
                "nodes": args.get("nodes", existing_workflow.nodes),
                "connections": args.get("connections", existing_workflow.connections),
                "active": args.get("active", existing_workflow.active),
                "tags": args.get("tags", existing_workflow.tags)
            }
            
            workflow = WorkflowModel(**update_data)
            updated_workflow = await self.n8n_client.update_workflow(args["workflow_id"], workflow)
            
            result = {
                "success": True,
                "message": f"Workflow '{updated_workflow.name}' updated successfully",
                "workflow": {
                    "id": updated_workflow.id,
                    "name": updated_workflow.name,
                    "active": updated_workflow.active,
                    "nodes_count": len(updated_workflow.nodes)
                }
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error updating workflow: {str(e)}")]
    
    async def _handle_delete_workflow(self, args: dict) -> list[types.TextContent]:
        """Workflow silme handler'ı"""
        if "workflow_id" not in args:
            return [types.TextContent(type="text", text="Missing required field: workflow_id")]
        
        try:
            deleted = await self.n8n_client.delete_workflow(args["workflow_id"])
            
            if not deleted:
                return [types.TextContent(type="text", text=f"Workflow not found: {args['workflow_id']}")]
            
            result = {
                "success": True,
                "message": f"Workflow '{args['workflow_id']}' deleted successfully",
                "workflow_id": args["workflow_id"]
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error deleting workflow: {str(e)}")]
    
    async def _handle_activate_workflow(self, args: dict) -> list[types.TextContent]:
        """Workflow aktivasyon handler'ı"""
        if "workflow_id" not in args:
            return [types.TextContent(type="text", text="Missing required field: workflow_id")]
        
        try:
            activated = await self.n8n_client.activate_workflow(args["workflow_id"])
            
            if not activated:
                return [types.TextContent(type="text", text=f"Workflow not found: {args['workflow_id']}")]
            
            result = {
                "success": True,
                "message": f"Workflow '{args['workflow_id']}' activated successfully",
                "workflow_id": args["workflow_id"],
                "active": True
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error activating workflow: {str(e)}")]
    
    async def _handle_deactivate_workflow(self, args: dict) -> list[types.TextContent]:
        """Workflow deaktivasyon handler'ı"""
        if "workflow_id" not in args:
            return [types.TextContent(type="text", text="Missing required field: workflow_id")]
        
        try:
            deactivated = await self.n8n_client.deactivate_workflow(args["workflow_id"])
            
            if not deactivated:
                return [types.TextContent(type="text", text=f"Workflow not found: {args['workflow_id']}")]
            
            result = {
                "success": True,
                "message": f"Workflow '{args['workflow_id']}' deactivated successfully",
                "workflow_id": args["workflow_id"],
                "active": False
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error deactivating workflow: {str(e)}")]
    
    async def _handle_health_check(self, args: dict) -> list[types.TextContent]:
        """Health check handler'ı"""
        try:
            is_healthy = await self.n8n_client.health_check()
            
            result = {
                "success": True,
                "healthy": is_healthy,
                "message": "n8n API is accessible" if is_healthy else "n8n API is not accessible",
                "endpoint": self.n8n_client.base_url
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]
            
        except Exception as e:
            result = {
                "success": False,
                "healthy": False,
                "error": str(e),
                "endpoint": self.n8n_client.base_url if self.n8n_client else "Unknown"
            }
            
            return [types.TextContent(type="text", text=json.dumps(result))]


async def main():
    """Ana sunucu fonksiyonu"""
    try:
        # Konfigürasyonu yükle
        settings = None
        
        # Komut satırı argümanlarını kontrol et
        config_path = None
        use_env = False
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "--env":
                use_env = True
            else:
                config_path = sys.argv[1]
        
        try:
            settings = load_settings(config_path=config_path, use_env=use_env)
        except Exception as e:
            print(f"Configuration error: {e}")
            print("Usage:")
            print("  python -m src.n8n_mcp.server [config_path]")
            print("  python -m src.n8n_mcp.server --env")
            sys.exit(1)
        
        # Logging'i ayarla
        setup_logging(settings.logging)
        logger.info("Starting n8n MCP Server", version=settings.mcp.version)
        
        # Konfigürasyonu doğrula
        if not settings.validate_n8n_connection():
            logger.error("Invalid n8n configuration")
            sys.exit(1)
        
        # Sunucuyu başlat
        async with N8nMcpServer(settings) as mcp_server:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("n8n MCP Server started and ready for connections")
                
                await mcp_server.server.run(
                    read_stream,
                    write_stream,
                    NotificationOptions()
                )
                
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
