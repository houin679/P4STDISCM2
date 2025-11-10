import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const mockGrades = [
  { course: "CS101", semester: "Fall 2023", grade: "A-", credits: 3 },
  { course: "MA101", semester: "Fall 2023", grade: "B+", credits: 4 },
  { course: "PH100", semester: "Spring 2024", grade: "A", credits: 3 },
  { course: "DS310", semester: "Spring 2024", grade: "In Progress", credits: 4 },
];

const Grades = () => {
  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">My Grades</h1>
      <Card>
        <CardHeader>
          <CardTitle>Academic Transcript</CardTitle>
          <CardDescription>A summary of your completed and in-progress courses.</CardDescription>
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
              {mockGrades.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{item.course}</TableCell>
                  <TableCell>{item.semester}</TableCell>
                  <TableCell>{item.credits}</TableCell>
                  <TableCell className={`text-right font-semibold ${item.grade === "In Progress" ? "text-muted-foreground" : "text-primary"}`}>
                    {item.grade}
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

export default Grades;