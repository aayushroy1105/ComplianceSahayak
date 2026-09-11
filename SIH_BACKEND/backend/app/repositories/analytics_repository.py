from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Dict, Any

from app.models.manufacturer import Manufacturer
from app.models.inspection import Inspection
from app.models.violation import Violation

async def get_repeat_offender_analytics(db: AsyncSession) -> List[Dict[str, Any]]:
    # 1. Base stats per manufacturer
    # We outer join to include manufacturers with 0 inspections, or inner join if we only want offenders.
    # The requirement is "repeat-offenders", so let's only include those with inspections.
    stats_query = (
        select(
            Manufacturer.id.label('manufacturer_id'),
            Manufacturer.name.label('manufacturer_name'),
            func.count(func.distinct(Inspection.id)).label('total_inspections'),
            func.count(func.distinct(Violation.id)).label('total_violations'),
            func.max(Inspection.inspection_date).label('latest_inspection')
        )
        .select_from(Manufacturer)
        .join(Inspection, Inspection.manufacturer_id == Manufacturer.id)
        .outerjoin(Violation, Violation.inspection_id == Inspection.id)
        .group_by(Manufacturer.id)
    )
    
    stats_result = await db.execute(stats_query)
    manufacturers_stats = {
        row.manufacturer_id: {
            "manufacturer_id": row.manufacturer_id,
            "manufacturer_name": row.manufacturer_name,
            "total_inspections": row.total_inspections,
            "total_violations": row.total_violations,
            "latest_inspection": row.latest_inspection,
            "repeat_violation_count": 0,
            "top_violation_codes": []
        }
        for row in stats_result.all()
    }
    
    # 2. Violation frequencies per manufacturer
    freq_query = (
        select(
            Inspection.manufacturer_id,
            Violation.violation_code,
            func.count(func.distinct(Inspection.id)).label('inspection_count')
        )
        .select_from(Violation)
        .join(Inspection, Inspection.id == Violation.inspection_id)
        .where(Inspection.manufacturer_id.isnot(None))
        .group_by(Inspection.manufacturer_id, Violation.violation_code)
    )
    
    freq_result = await db.execute(freq_query)
    
    # Process frequencies
    from collections import defaultdict
    freqs = defaultdict(list)
    
    for row in freq_result.all():
        m_id = row.manufacturer_id
        code = row.violation_code
        count = row.inspection_count
        
        freqs[m_id].append({"code": code, "count": count})
        
        if count > 1:
            # It's a repeat violation
            if m_id in manufacturers_stats:
                manufacturers_stats[m_id]["repeat_violation_count"] += 1
                
    # Assign top violations and compliance summary
    analytics_list = []
    for m_id, stats in manufacturers_stats.items():
        m_freqs = freqs.get(m_id, [])
        # Sort by count desc
        m_freqs.sort(key=lambda x: x["count"], reverse=True)
        stats["top_violation_codes"] = [f["code"] for f in m_freqs[:3]]  # top 3
        
        # Calculate summary
        ratio = stats["total_violations"] / stats["total_inspections"] if stats["total_inspections"] > 0 else 0
        if ratio == 0:
            stats["compliance_summary"] = "EXCELLENT"
        elif ratio < 1:
            stats["compliance_summary"] = "GOOD"
        elif ratio < 2:
            stats["compliance_summary"] = "AVERAGE"
        else:
            stats["compliance_summary"] = "POOR"
            
        analytics_list.append(stats)
        
    # Sort analytics list by repeat violations desc, total violations desc
    analytics_list.sort(key=lambda x: (x["repeat_violation_count"], x["total_violations"]), reverse=True)
    
    return analytics_list
