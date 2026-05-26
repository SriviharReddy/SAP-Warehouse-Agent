import asyncio
from langchain_core.tools import tool

@tool
async def async_get_stock_level(warehouse_id: str, item_id: str) -> dict:
    """Retrieve the current inventory stock level, unit of measure, and specific storage bin locations 
    for an item inside a given SAP warehouse.
    
    Args:
        warehouse_id (str): The ID of the SAP warehouse (e.g., 'WH-101', 'WH-202').
        item_id (str): The material/item SKU number (e.g., 'SKU-8892', 'SKU-3120').
    """
    await asyncio.sleep(0.5)  # Simulate async SAP network call
    
    # Mock database lookup
    mock_data = {
        "SKU-8892": {"quantity": 1250, "uom": "EA", "bins": ["B-101", "B-102"]},
        "SKU-3120": {"quantity": 420, "uom": "BOX", "bins": ["B-402"]},
        "SKU-7751": {"quantity": 0, "uom": "EA", "bins": []}
    }
    
    stock_info = mock_data.get(item_id, {"quantity": 15, "uom": "EA", "bins": ["B-TEMP"]})
    return {
        "status": "SUCCESS",
        "warehouse_id": warehouse_id,
        "item_id": item_id,
        "total_quantity": stock_info["quantity"],
        "unit_of_measure": stock_info["uom"],
        "bin_locations": stock_info["bins"]
    }

@tool
async def async_get_storage_bin_info(bin_id: str) -> dict:
    """Get the environmental constraints, dimensions, current capacity utilization, 
    and list of SKUs currently stored inside a specific warehouse storage bin in SAP.
    
    Args:
        bin_id (str): The ID of the storage bin (e.g., 'B-101', 'B-402').
    """
    await asyncio.sleep(0.5)
    
    # Mock storage bin properties
    bins = {
        "B-101": {"type": "Standard", "temp": "Ambient", "max_capacity": 5000, "utilization": 0.45, "skus": ["SKU-8892"]},
        "B-102": {"type": "Standard", "temp": "Ambient", "max_capacity": 5000, "utilization": 0.12, "skus": ["SKU-8892"]},
        "B-402": {"type": "Cold Storage", "temp": "Frozen (-18C)", "max_capacity": 2000, "utilization": 0.88, "skus": ["SKU-3120"]}
    }
    
    bin_info = bins.get(bin_id, {"type": "Standard", "temp": "Ambient", "max_capacity": 1000, "utilization": 0.0, "skus": []})
    return {
        "status": "SUCCESS",
        "bin_id": bin_id,
        "bin_type": bin_info["type"],
        "temperature_setting": bin_info["temp"],
        "capacity_utilization": f"{bin_info['utilization'] * 100}%",
        "stored_skus": bin_info["skus"]
    }

@tool
async def async_list_inbound_deliveries(warehouse_id: str) -> list:
    """Retrieve a list of scheduled inbound freight shipments, purchase orders, 
    and planned deliveries expected to arrive at a warehouse today.
    
    Args:
        warehouse_id (str): The warehouse ID to query (e.g., 'WH-101').
    """
    await asyncio.sleep(0.5)
    
    return [
        {
            "delivery_id": "INB-99821",
            "source": "SAP-PO-4482",
            "carrier": "DHL Freight",
            "eta": "14:30",
            "status": "IN_TRANSIT"
        },
        {
            "delivery_id": "INB-99825",
            "source": "SAP-PO-9912",
            "carrier": "FedEx Custom",
            "eta": "16:00",
            "status": "PENDING"
        }
    ]

@tool
async def async_get_inbound_delivery_details(delivery_id: str) -> dict:
    """Retrieve specific detailed information for an inbound delivery shipment, including 
    line items, supplier name, receiving dock door, and special handling instructions in SAP.
    
    Args:
        delivery_id (str): The unique ID of the inbound delivery (e.g., 'INB-99821', 'INB-99825').
    """
    await asyncio.sleep(0.5)
    
    deliveries = {
        "INB-99821": {
            "supplier": "Acme Global Manufacturing",
            "dock_door": "DOCK-04",
            "handling_instructions": "Fragile items. Handle with care. Place in Standard Ambient bins.",
            "line_items": [{"sku": "SKU-8892", "quantity": 500, "uom": "EA", "description": "High-grade Steel Brackets"}]
        },
        "INB-99825": {
            "supplier": "ColdChain Logistics Inc",
            "dock_door": "DOCK-09 (Cold Dock)",
            "handling_instructions": "Temperature sensitive. Move immediately to Cold Storage bins.",
            "line_items": [{"sku": "SKU-3120", "quantity": 100, "uom": "BOX", "description": "Cryogenic Thermometer Modules"}]
        }
    }
    
    details = deliveries.get(delivery_id, {
        "supplier": "Unknown Supplier",
        "dock_door": "DOCK-UNASSIGNED",
        "handling_instructions": "Standard receiving procedures apply.",
        "line_items": []
    })
    return {
        "status": "SUCCESS",
        "delivery_id": delivery_id,
        **details
    }

@tool
async def async_list_outbound_orders(warehouse_id: str) -> list:
    """List pending outbound customer shipping orders that are currently scheduled for 
    picking, packing, and dispatch from a warehouse.
    
    Args:
        warehouse_id (str): The warehouse ID to query (e.g., 'WH-101').
    """
    await asyncio.sleep(0.5)
    
    return [
        {
            "order_id": "ORD-5501",
            "destination": "Client Tokyo Ltd",
            "scheduled_ship": "18:00",
            "status": "AWAITING_PICK"
        },
        {
            "order_id": "ORD-5502",
            "destination": "VaporRetail Inc",
            "scheduled_ship": "20:00",
            "status": "PICKING"
        }
    ]

@tool
async def async_get_outbound_order_details(order_id: str) -> dict:
    """Retrieve deep detailed info about an outbound order including the ordered line items, 
    quantities, exact delivery address, freight carrier class, and priority rank in SAP.
    
    Args:
        order_id (str): The unique ID of the outbound order (e.g., 'ORD-5501', 'ORD-5502').
    """
    await asyncio.sleep(0.5)
    
    orders = {
        "ORD-5501": {
            "recipient": "Client Tokyo Ltd, Shinjuku District, Tokyo",
            "carrier_class": "Next Day Express",
            "priority": "HIGH",
            "line_items": [{"sku": "SKU-8892", "quantity": 150, "uom": "EA", "description": "High-grade Steel Brackets"}]
        },
        "ORD-5502": {
            "recipient": "VaporRetail Inc, Distribution Hub, Berlin",
            "carrier_class": "Standard Economy LTL",
            "priority": "MEDIUM",
            "line_items": [{"sku": "SKU-3120", "quantity": 25, "uom": "BOX", "description": "Cryogenic Thermometer Modules"}]
        }
    }
    
    details = orders.get(order_id, {
        "recipient": "Unknown Customer",
        "carrier_class": "Standard",
        "priority": "LOW",
        "line_items": []
    })
    return {
        "status": "SUCCESS",
        "order_id": order_id,
        **details
    }

@tool
async def async_get_picking_task_details(task_id: str) -> dict:
    """Get the current progress status, assigned worker, source storage bins, target staging area, 
    and target picking lists for an active picking task in SAP.
    
    Args:
        task_id (str): The ID of the picking task (e.g., 'TSK-SAP-98124', 'TSK-SAP-44120').
    """
    await asyncio.sleep(0.5)
    
    tasks = {
        "TSK-SAP-98124": {
            "assigned_worker": "Worker-04 (Kenji S.)",
            "status": "IN_PROGRESS",
            "progress": "45%",
            "source_bins": ["B-101", "B-102"],
            "target_staging": "STAGING-AREA-02",
            "items": [{"sku": "SKU-8892", "quantity": 150, "uom": "EA"}]
        },
        "TSK-SAP-44120": {
            "assigned_worker": "Worker-11 (Marta H.)",
            "status": "QUEUED",
            "progress": "0%",
            "source_bins": ["B-402"],
            "target_staging": "STAGING-AREA-09 (COLD DOCK)",
            "items": [{"sku": "SKU-3120", "quantity": 25, "uom": "BOX"}]
        }
    }
    
    details = tasks.get(task_id, {
        "assigned_worker": "Worker-Unassigned",
        "status": "NOT_FOUND",
        "progress": "0%",
        "source_bins": [],
        "target_staging": "STAGING-UNASSIGNED",
        "items": []
    })
    return {
        "status": "SUCCESS",
        "task_id": task_id,
        **details
    }

# Export all tools in a clean array (strictly read/get-info only)
sap_tools = [
    async_get_stock_level,
    async_get_storage_bin_info,
    async_list_inbound_deliveries,
    async_get_inbound_delivery_details,
    async_list_outbound_orders,
    async_get_outbound_order_details,
    async_get_picking_task_details
]
