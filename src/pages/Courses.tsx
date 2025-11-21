import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { showSuccess, showError } from "@/utils/toast";
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

interface Course { id: number; code?: string; name: string; instructor?: string; capacity?: number }

async function fetchCourses() {
  const res = await api.apiFetch('/api/courses');
  if (!res.ok) throw new Error('Failed to fetch courses');
  return res.json();
}

const Courses = () => {
  const qc = useQueryClient();
  const { data: courses, isLoading } = useQuery({ queryKey: ['courses'], queryFn: fetchCourses });

  const handleEnroll = async (courseId: number, courseName: string) => {
    try {
      const res = await api.apiFetch(`/api/courses/${courseId}/enroll`, { method: 'POST' });
      if (!res.ok) {
        showError('Enroll failed');
        return;
      }
      showSuccess(`Successfully enrolled in ${courseName}!`);
      qc.invalidateQueries({ queryKey: ['courses'] });
    } catch (e) {
      showError('Enroll failed');
    }
  };

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">Course Catalog</h1>
      <Card>
        <CardHeader>
          <CardTitle>Available Courses</CardTitle>
          <CardDescription>View courses and manage your enrollment.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">Course ID</TableHead>
                <TableHead>Course Name</TableHead>
                <TableHead>Instructor</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={4}>Loading...</TableCell></TableRow>
              ) : (courses || []).length === 0 ? (
                <TableRow><TableCell colSpan={4}>No courses available</TableCell></TableRow>
              ) : (courses || []).map((course: Course) => (
                <TableRow key={course.id}>
                  <TableCell className="font-medium">{course.code ?? course.id}</TableCell>
                  <TableCell>{course.name}</TableCell>
                  <TableCell>{course.instructor}</TableCell>
                  <TableCell className="text-right">
                    <Button onClick={() => handleEnroll(course.id, course.name)}>
                      Enroll
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Layout>
  );
};

export default Courses;