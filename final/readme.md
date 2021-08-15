A somewhat sloppy implementation of a course database for students and instructors.

Each user on registration is prompted to choose the "type" of user that they are, ie a student or instructor
And depending on their choice, will give them access to "type" specific pages.
If users of either type try to access pages that are not for them, they are given a prompt stating so.

The ids of students and instructors are stored separately in different databases, each with the 
corresponding courses that the student is applied to or the courses an instructor has created.

Students who register or log in for the first time will be then redirected to a page where they will specify their year/level
Depending on this choice, they will gain access to courses that are meant for said level/year

By default students are given a balance of 20,000 USD to spend on applying to courses of varying prices.

Instructors on the other hand have the option of creating a course, on the condition that it doesn't already exist.
The instructor can also specify the subject, id, level/year and name of the course.

These courses are assigned a separate id as per the instructor's choice and this id will be referred to when displaying 
the page of courses for the students who are applied to it and the instructor who created it.

Also it is through this id how instructors are able to give grades and notes on each student 
applied to their courses.

Users are also given the choice to change their password.

Students who already applied to a course will not be allowed to apply to said course again