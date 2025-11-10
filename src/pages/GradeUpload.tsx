import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { showSuccess } from "@/utils/toast";

const mockFacultyCourses = [
  { id: "CS101", name: "Introduction to Programming" },
  { id: "DS310", name: "Distributed Systems" },
];

const GradeUpload = () => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Mock submission logic
    showSuccess("Grades submitted successfully! (Mock Action)");
  };

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">Faculty Grade Upload</h1>
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle>Upload Grades</CardTitle>
          <CardDescription>Select a course and paste or enter the student grades below.</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6">
            <div className="grid gap-2">
              <Label htmlFor="course-select">Select Course</Label>
              <Select required>
                <SelectTrigger id="course-select">
                  <SelectValue placeholder="Choose a course to upload grades for" />
                </SelectTrigger>
                <SelectContent>
                  {mockFacultyCourses.map((course) => (
                    <SelectItem key={course.id} value={course.id}>
                      {course.id} - {course.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="grade-data">Grade Data (e.g., StudentID, Grade)</Label>
              <Textarea
                id="grade-data"
                placeholder="Paste grade data here. Format: [StudentID],[Grade] per line."
                rows={10}
                required
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" className="w-full">
              Submit Grades to Node
            </Button>
          </CardFooter>
        </form>
      </Card>
    </Layout>
  );
};

export default GradeUpload;