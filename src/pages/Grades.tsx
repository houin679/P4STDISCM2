import { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import api from "@/lib/api";

interface Grade {
  id: number;
  course_id: number;
  grade_value: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
}

const Grades = () => {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [courses, setCourses] = useState<Record<number, Course>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch grades
        const resGrades = await api.apiFetch("/api/student/me/grades");
        if (!resGrades.ok) {
          console.error("Failed to fetch grades:", resGrades.status);
          return;
        }
        const gradeData: Grade[] = await resGrades.json();
        setGrades(gradeData);

        // Fetch courses for lookup
        const resCourses = await api.apiFetch("/api/courses");
        if (!resCourses.ok) {
          console.error("Failed to fetch courses list");
          return;
        }
        const courseData: Course[] = await resCourses.json();

        // Build lookup dictionary
        const lookup: Record<number, Course> = {};
        for (const c of courseData) lookup[c.id] = c;
        setCourses(lookup);

      } catch (err) {
        console.error("Error fetching grades or courses:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <h1 className="text-3xl font-bold mb-6">My Grades</h1>
        <p>Loading grades…</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">My Grades</h1>
      <Card>
        <CardHeader>
          <CardTitle>Academic Transcript</CardTitle>
          <CardDescription>Your completed and in-progress courses.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Course</TableHead>
                <TableHead>Semester</TableHead>
                <TableHead>Credits</TableHead>
                <TableHead className="text-right">Grade</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {grades.map((item) => {
                const course = courses[item.course_id];
                return (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">
                      {course ? `${course.code} - ${course.name}` : `Course ${item.course_id}`}
                    </TableCell>

                    <TableCell>Term 1</TableCell>
                    <TableCell>3</TableCell>

                    <TableCell
                      className={`text-right font-semibold ${
                        item.grade_value === "In Progress"
                          ? "text-muted-foreground"
                          : "text-primary"
                      }`}
                    >
                      {item.grade_value}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Layout>
  );
};

export default Grades;
