import asyncio
from celery_app import celery_app
from database import AsyncSessionLocal
from services_v2.preprocessor import PreprocessorService
from services.orchestrator import OrchestratorService
from sqlalchemy import select
from models_v2 import SecuritySignal, IncidentMemory

async def run_process_file(file_path, context_info):
    async with AsyncSessionLocal() as session:
        signals, stats = await PreprocessorService.process_file(file_path, session)
        return {"signals_count": len(signals), "stats": stats}

@celery_app.task(name="process_file_task")
def process_file_task(file_path, context_info):
    return asyncio.run(run_process_file(file_path, context_info))

async def run_process_batch(batch_data, context_info):
    """
    Process a batch of logs received from API.
    """
    async with AsyncSessionLocal() as session:
        # Re-using Preprocessor Service logic but adapted for memory list
        # We need to extend PreprocessorService to handle list vs file
        # For now, let's implement a direct handler here to keep it simple or call a new method
        
        from services_v2.preprocessor import DynamicLogAnalyzer
        analyzer = DynamicLogAnalyzer()
        
        logs = batch_data.get('logs', [])
        source_system = batch_data.get('source_system')
        
        processed_count = 0
        for log in logs:
            raw_msg = log.get('raw_message')
            if raw_msg:
                # Inject source system into the line if needed, or handle in metadata
                # Analyzer expects string line
                analyzer.process_line(raw_msg)
                processed_count += 1
        
        # Generate Signals (Phase 4-8)
        # Note: This might be heavy for a single HTTP batch if batch is huge.
        # Ideally, we dump to raw_logs table first, then process.
        # But per requirements: "Immediately enqueue logs for downstream processing"
        
        final_signals = await analyzer.generate_signals(session)
        
        # Save signals
        for s in final_signals:
            session.add(s)
        await session.commit()
        
        return {
            "processed": processed_count,
            "signals_generated": len(final_signals),
            "job_id": context_info.get("job_id")
        }

@celery_app.task(name="process_log_batch_task")
def process_log_batch_task(batch_data, context_info):
    return asyncio.run(run_process_batch(batch_data, context_info))

async def run_orchestrate(signal_id):
    async with AsyncSessionLocal() as session:
        # Fetch signal
        res = await session.execute(select(SecuritySignal).where(SecuritySignal.id == signal_id))
        signal = res.scalars().first()
        if not signal:
            return {"error": "Signal not found"}
            
        # Mock context for now or fetch from IncidentMemory
        context = {"short_term": {"active_context": [signal.to_dict()]}}
        results = await OrchestratorService.orchestrate([signal.to_dict()], context)
        return results

@celery_app.task(name="orchestrate_task")
def orchestrate_task(signal_id):
    return asyncio.run(run_orchestrate(signal_id))
