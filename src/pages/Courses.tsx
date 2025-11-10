import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { showSuccess } from "@/utils/toast";

const mockCourses = [
  { id: "CS101", name: "Introduction to Programming", instructor: "Dr. Smith", enrolled: true },
  { id: "MA205", name: "Calculus III", instructor: "Prof. Jones", enrolled: false },
  { id: "DS310", name: "Distributed Systems", instructor: "Dr. Dyad", enrolled: true },
  { id: "PH100", name: "Physics Fundamentals", instructor: "Prof. Lee", enrolled: false },
];

const Courses = () => {
  const handleEnroll = (courseName: string) => {
    showSuccess(`Successfully enrolled in ${courseName}! (Mock Action)`);
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
              {mockCourses.map((course) => (
                <TableRow key={course.id}>
                  <TableCell className="font-medium">{course.id}</TableCell>
                  <TableCell>{course.name}</TableCell>
                  <TableCell>{course.instructor}</TableCell>
                  <TableCell className="text-right">
                    {course.enrolled ? (
                      <Button variant="secondary" disabled>
                        Enrolled
                      </Button>
                    ) : (
                      <Button onClick={() => handleEnroll(course.name)}>
                        Enroll
                      </Button>
                    )}
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