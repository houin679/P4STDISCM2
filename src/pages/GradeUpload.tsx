import React, { useState } from "react";
import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { showSuccess } from "@/utils/toast";
import { Trash2 } from "lucide-react";

interface GradeEntry {
  id: number;
  studentName: string;
  studentId: string;
  grade: string;
}

const mockFacultyCourses = [
  { id: "CS101", name: "Introduction to Programming" },
  { id: "DS310", name: "Distributed Systems" },
];

let nextId = 0;

const GradeUpload = () => {
  const [selectedCourse, setSelectedCourse] = useState<string | undefined>(undefined);
  const [gradeEntries, setGradeEntries] = useState<GradeEntry[]>([
    { id: nextId++, studentName: "", studentId: "", grade: "" },
  ]);

  const handleAddEntry = () => {
    setGradeEntries([...gradeEntries, { id: nextId++, studentName: "", studentId: "", grade: "" }]);
  };

  const handleRemoveEntry = (id: number) => {
    setGradeEntries(gradeEntries.filter(entry => entry.id !== id));
  };

  const handleInputChange = (id: number, field: keyof Omit<GradeEntry, 'id'>, value: string) => {
    setGradeEntries(gradeEntries.map(entry => 
      entry.id === id ? { ...entry, [field]: value } : entry
    ));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCourse) {
      alert("Please select a course.");
      return;
    }
    
    const validEntries = gradeEntries.filter(entry => 
      entry.studentName.trim() && entry.studentId.trim() && entry.grade.trim()
    );

    if (validEntries.length === 0) {
      alert("Please enter at least one complete grade entry.");
      return;
    }

    console.log("Submitting grades for course:", selectedCourse);
    console.log("Grade Data:", validEntries);
    
    // Mock submission logic
    showSuccess(`Grades for ${selectedCourse} submitted successfully! (Mock Action)`);
    
    // Reset form after submission
    setSelectedCourse(undefined);
    setGradeEntries([{ id: nextId++, studentName: "", studentId: "", grade: "" }]);
  };

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">Faculty Grade Upload</h1>
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Upload Grades</CardTitle>
          <CardDescription>Select a course and enter student grades below.</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6">
            <div className="grid gap-2">
              <Label htmlFor="course-select">Select Course</Label>
              <Select 
                required 
                value={selectedCourse} 
                onValueChange={setSelectedCourse}
              >
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

            <div className="space-y-4">
              <h3 className="text-lg font-semibold border-b pb-2">Grade Data Entries</h3>
              
              <div className="grid grid-cols-12 gap-4 font-medium text-sm text-muted-foreground pb-2 border-b">
                <div className="col-span-5">Student Name</div>
                <div className="col-span-3">Student ID</div>
                <div className="col-span-3">Grade (e.g., A, B+, C-)</div>
                <div className="col-span-1"></div> {/* Action column */}
              </div>

              {gradeEntries.map((entry, index) => (
                <div key={entry.id} className="grid grid-cols-12 gap-4 items-center">
                  <div className="col-span-5">
                    <Input
                      placeholder="Student Name"
                      value={entry.studentName}
                      onChange={(e) => handleInputChange(entry.id, 'studentName', e.target.value)}
                      required
                    />
                  </div>
                  <div className="col-span-3">
                    <Input
                      placeholder="ID"
                      value={entry.studentId}
                      onChange={(e) => handleInputChange(entry.id, 'studentId', e.target.value)}
                      required
                    />
                  </div>
                  <div className="col-span-3">
                    <Input
                      placeholder="Grade"
                      value={entry.grade}
                      onChange={(e) => handleInputChange(entry.id, 'grade', e.target.value)}
                      required
                    />
                  </div>
                  <div className="col-span-1 flex justify-end">
                    {gradeEntries.length > 1 && (
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        type="button"
                        onClick={() => handleRemoveEntry(entry.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              
              <Button type="button" variant="secondary" onClick={handleAddEntry} className="w-full mt-4">
                Add Another Student
              </Button>
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