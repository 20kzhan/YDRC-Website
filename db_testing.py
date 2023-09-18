import asqlite
import asyncio

async def main():
    async with asqlite.connect('YDRC.db') as conn:
        async with conn.cursor() as cursor:
            # await cursor.execute("CREATE TABLE teachers (teacher_id INTEGER PRIMARY KEY, teacher_name TEXT, teacher_email TEXT)")
            # await cursor.execute("CREATE TABLE classes (class_id INTEGER PRIMARY KEY, teacher_id INTEGER, class_name TEXT, FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id))")
            # await cursor.execute("CREATE TABLE students (student_id INTEGER PRIMARY KEY, student_name TEXT, student_email TEXT, student_dob TEXT, parent_wechat TEXT, parent_email TEXT, class_id INTEGER, FOREIGN KEY (class_id) REFERENCES classes (class_id))")

            await conn.commit()

asyncio.run(main())