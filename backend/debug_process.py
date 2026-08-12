import asyncio
import os
from app.services.processing_service import ProcessingService
from app.services.llm import create_llm_provider
from app.services.storage_service import StorageService
from app.repositories.course_repository import CourseRepository
from app.repositories.content_repository import ContentRepository

async def debug_process():
    # Replace this with the course_id from the screenshot/db
    repo = CourseRepository()
    courses = await repo.list_courses()
    if not courses:
        print("No courses found!")
        return
    
    course_id = courses[-1].id
    print(f"Processing course: {course_id} - {courses[-1].name}")
    
    llm = create_llm_provider()
    storage = StorageService()
    content_repo = ContentRepository()
    
    service = ProcessingService(llm, storage, repo, content_repo)
    result = await service.process_course(course_id)
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(debug_process())
