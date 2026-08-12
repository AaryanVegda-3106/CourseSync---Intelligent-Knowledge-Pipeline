import asyncio
from app.repositories.course_repository import CourseRepository

async def test_delete():
    repo = CourseRepository()
    courses = await repo.list_courses()
    for course in courses:
        print(f"Trying to delete {course.id}")
        try:
            res = await repo.delete_course(course.id)
            print("Delete result:", res)
        except Exception as e:
            print("Delete failed:", e)

if __name__ == "__main__":
    asyncio.run(test_delete())
