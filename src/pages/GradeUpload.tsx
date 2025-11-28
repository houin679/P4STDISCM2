import React, { useState } from "react";
import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { showSuccess, showError } from "@/utils/toast";
import { Trash2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import api from '@/lib/api';

interface GradeEntry {
  id: number;
  studentName: string;
  studentId: string;
  grade: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
}

interface User {
  id: number;
  username: string;
}

let nextId = 0;

async function fetchCourses() {
  const res = await api.apiFetch('/api/courses');
  if (!res.ok) throw new Error('Failed to fetch courses');
  return res.json();
}

async function fetchUsers() {
  const res = await api.apiFetch('/api/users');
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

const GradeUpload = () => {
  const { data: courses = [] } = useQuery({ queryKey: ['courses'], queryFn: fetchCourses });
  const { data: users = [] } = useQuery({ queryKey: ['users'], queryFn: fetchUsers });

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

  const handleStudentSelect = (id: number, username: string, userId: number) => {
    setGradeEntries(gradeEntries.map(entry =>
      entry.id === id ? { ...entry, studentName: username, studentId: String(userId) } : entry
    ));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedCourse) {
      showError("Please select a course.");
      return;
    }

    const validEntries = gradeEntries.filter(entry =>
      entry.studentName.trim() && entry.studentId.trim() && entry.grade.trim()
    );

    if (validEntries.length === 0) {
      showError("Please enter at least one complete grade entry.");
      return;
    }

    (async () => {
      try {
        const payload = {
          entries: validEntries.map(v => ({
            student_id: Number(v.studentId),
            grade_value: v.grade
          }))
        };

        const res = await api.apiFetch(
          `/api/faculty/courses/${Number(selectedCourse)}/grades`,
          {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' }
          }
        );

        if (!res.ok) {
          showError('Failed to upload grades');
          return;
        }

        showSuccess("Grades submitted successfully!");
        setSelectedCourse(undefined);
        setGradeEntries([{ id: nextId++, studentName: "", studentId: "", grade: "" }]);
      } catch (err) {
        showError('Failed to upload grades');
      }
    })();
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
            {/* Course Selection */}
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
                  {courses.map((course: Course) => (
                    <SelectItem key={course.id} value={String(course.id)}>
                      {course.code} - {course.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Grade Entries */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold border-b pb-2">Grade Entries</h3>
              <div className="grid grid-cols-12 gap-4 font-medium text-sm text-muted-foreground pb-2 border-b">
                <div className="col-span-5">Student Name</div>
                <div className="col-span-3">Student ID</div>
                <div className="col-span-3">Grade</div>
                <div className="col-span-1"></div>
              </div>

              {gradeEntries.map((entry) => (
                <div key={entry.id} className="grid grid-cols-12 gap-4 items-center">
                  <div className="col-span-5">
                    <Select
                      value={entry.studentId}
                      onValueChange={(userId) => {
                        const user = (users as User[]).find(u => String(u.id) === userId);
                        if (user) handleStudentSelect(entry.id, user.username, user.id);
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select student" />
                      </SelectTrigger>
                      <SelectContent>
                        {(users as User[]).map((user) => (
                          <SelectItem key={user.id} value={String(user.id)}>
                            {user.username}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="col-span-3">
                    <Input value={entry.studentId} readOnly className="bg-muted" />
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
                      <Button variant="ghost" size="icon" type="button" onClick={() => handleRemoveEntry(entry.id)}>
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
            <Button type="submit" className="w-full">Submit Grades</Button>
          </CardFooter>
        </form>
      </Card>
    </Layout>
  );
};

export default GradeUpload;
