import asqlite
import asyncio

async def main():
    async with asqlite.connect('YDRC.db') as conn:
        async with conn.cursor() as cursor:
            # await cursor.execute("CREATE TABLE teachers (teacher_id TEXT PRIMARY KEY, teacher_name TEXT, teacher_email TEXT)")
            # await cursor.execute("CREATE TABLE classes (class_id INTEGER PRIMARY KEY, teacher_id TEXT, class_name TEXT, teacher_intro TEXT, class_schedule TEXT, class_description TEXT, class_plan TEXT, class_requirements TEXT, other_notes TEXT, FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id))")
            # await cursor.execute("CREATE TABLE students (student_id TEXT PRIMARY KEY, student_name TEXT, student_email TEXT, student_dob TEXT, parent_wechat TEXT, parent_email TEXT, class_id INTEGER)")
            # await cursor.execute("CREATE TABLE admins (admin_id TEXT PRIMARY KEY, admin_name TEXT, admin_email TEXT)")
            # await cursor.execute("DROP TABLE classes")
            # await cursor.execute("DROP TABLE enrollemnts")
            # await cursor.execute("DELETE FROM students") 
            # await cursor.execute("DELETE FROM classes")
            # await cursor.execute("DELETE FROM teachers")
            # await cursor.execute("DELETE FROM admins")
            # await cursor.execute("DELETE FROM teacher_temp")
            # await cursor.execute("INSERT INTO admins SELECT student_id, student_name, student_email FROM students WHERE student_id = 'auth0|6589f965ccba5f154af07083'")
            # await cursor.execute("ALTER TABLE admins ADD COLUMN active INTEGER")
            # await cursor.execute("UPDATE teachers SET teacher_classes = ? WHERE teacher_id = ?", ('7148176391558983680,0,0,0,0', 'auth0|6594e901dca1222f3d0bc536'))
            # await cursor.execute("UPDATE admins SET admin_email = ? WHERE admin_id = ?", ('email2@example.com', 'auth0|65862c5cfedc0dfecbe04d62'))
            # await cursor.execute("UPDATE students SET class_id = ? WHERE student_id = ?", ('0,0,0,0,0', 'auth0|6594e8adb060ed59167e044d'))
            # await cursor.execute("UPDATE classes SET students = ? WHERE class_id = ?", ("auth0|65921035dca1222f3d0a475e", 7147008449672704000))
            # await cursor.execute("ALTER TABLE classes ADD COLUMN students TEXT")
            
            # await cursor.execute("ALTER TABLE classes RENAME TO classes_old")
            # await cursor.execute("CREATE TABLE classes (class_id INTEGER PRIMARY KEY, teacher_id TEXT, class_name TEXT, teacher_intro TEXT, class_schedule TEXT, class_description TEXT, class_plan TEXT, class_requirements TEXT, other_notes TEXT, students JSON, FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id))")
            # await cursor.execute("INSERT INTO classes (class_id, teacher_id, class_name, teacher_intro, class_schedule, class_description, class_plan, class_requirements, other_notes, students) SELECT class_id, teacher_id, class_name, teacher_intro, class_schedule, class_description, class_plan, class_requirements, other_notes, json('{}') FROM classes_old")
            # await cursor.execute("DROP TABLE classes_old")
            # await cursor.execute("DELETE FROM students")

            # await cursor.execute("CREATE TABLE teacher_temp (teacher_id TEXT PRIMARY KEY, teacher_name TEXT, teacher_email TEXT)")

            await cursor.execute("CREATE TABLE enrollements (enrollment_id INTEGER PRIMARY KEY, student_id TEXT, class_id INTEGER, points INTEGER, FOREIGN KEY (student_id) REFERENCES students (student_id), FOREIGN KEY (class_id) REFERENCES classes (class_id))")

            await cursor.execute("ALTER TABLE enrollements ADD COLUMN approved TEXT")

            await conn.commit()

asyncio.run(main())
