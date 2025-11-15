import React, { useState } from "react";
import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { showSuccess, showError } from "@/utils/toast";
import { Plus, Trash2, Edit, Lock } from "lucide-react";

interface Course {
  id: string;
  name: string;
  instructor: string;
  capacity: number;
}

const initialMockCourses: Course[] = [
  { id: "CS101", name: "Introduction to Programming", instructor: "Dr. Smith", capacity: 50 },
  { id: "MA205", name: "Calculus III", instructor: "Prof. Jones", capacity: 40 },
  { id: "DS310", name: "Distributed Systems", instructor: "Dr. Dyad", capacity: 30 },
];

// Mock identity of the currently logged-in faculty member for authorization checks
const CURRENT_FACULTY_ID = "Dr. Dyad";

const FacultyCourseManagement = () => {
  const [courses, setCourses] = useState<Course[]>(initialMockCourses);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [formState, setFormState] = useState<Omit<Course, 'id'> & { id: string }>({
    id: "",
    name: "",
    instructor: CURRENT_FACULTY_ID, // Default new courses to the current faculty
    capacity: 0,
  });

  React.useEffect(() => {
    if (editingCourse) {
      setFormState(editingCourse);
    } else {
      setFormState({ id: "", name: "", instructor: CURRENT_FACULTY_ID, capacity: 0 });
    }
  }, [editingCourse]);

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormState(prev => ({
      ...prev,
      [id]: id === 'capacity' ? parseInt(value) || 0 : value,
    }));
  };

  const handleSaveCourse = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formState.id || !formState.name || !formState.instructor || formState.capacity <= 0) {
      showError("Please fill in all fields correctly.");
      return;
    }
    
    // Authorization check: Only allow saving if the instructor is the current faculty or if it's a new course
    if (editingCourse && editingCourse.instructor !== CURRENT_FACULTY_ID) {
        showError("Authorization failed: You can only edit courses you teach.");
        setIsDialogOpen(false);
        setEditingCourse(null);
        return;
    }
    
    // Ensure the instructor field is set to the current faculty ID when adding/editing
    const courseToSave = { ...formState, instructor: CURRENT_FACULTY_ID, capacity: Number(formState.capacity) };


    if (editingCourse) {
      // Edit existing course
      setCourses(courses.map(c => c.id === editingCourse.id ? courseToSave : c));
      showSuccess(`Course ${formState.id} updated successfully! (Mock Action)`);
    } else {
      // Add new course
      if (courses.some(c => c.id === formState.id)) {
        showError(`Course ID ${formState.id} already exists.`);
        return;
      }
      setCourses([...courses, courseToSave]);
      showSuccess(`Course ${formState.id} added successfully! (Mock Action)`);
    }

    setIsDialogOpen(false);
    setEditingCourse(null);
  };

  const handleDeleteCourse = (courseId: string, instructor: string) => {
    if (instructor !== CURRENT_FACULTY_ID) {
        showError("Authorization failed: You can only delete courses you teach.");
        return;
    }
    
    if (confirm(`Are you sure you want to delete course ${courseId}?`)) {
      setCourses(courses.filter(c => c.id !== courseId));
      showSuccess(`Course ${courseId} deleted successfully! (Mock Action)`);
    }
  };

  const openAddDialog = () => {
    setEditingCourse(null);
    setIsDialogOpen(true);
  };

  const openEditDialog = (course: Course) => {
    if (course.instructor !== CURRENT_FACULTY_ID) {
        showError("Authorization failed: You can only edit courses you teach.");
        return;
    }
    setEditingCourse(course);
    setIsDialogOpen(true);
  };

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">Course Catalog Management</h1>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-2xl font-bold">Current Courses (Logged in as {CURRENT_FACULTY_ID})</CardTitle>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={openAddDialog}>
                <Plus className="mr-2 h-4 w-4" /> Add New Course
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>{editingCourse ? "Edit Course" : "Add New Course"}</DialogTitle>
                <CardDescription>
                  {editingCourse ? `Editing course ${editingCourse.id}` : "Enter details for the new course."}
                </CardDescription>
              </DialogHeader>
              <form onSubmit={handleSaveCourse}>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="id" className="text-right">
                      Course ID
                    </Label>
                    <Input
                      id="id"
                      value={formState.id}
                      onChange={handleFormChange}
                      className="col-span-3"
                      required
                      disabled={!!editingCourse}
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right">
                      Name
                    </Label>
                    <Input
                      id="name"
                      value={formState.name}
                      onChange={handleFormChange}
                      className="col-span-3"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="instructor" className="text-right">
                      Instructor
                    </Label>
                    {/* Display the instructor name, but prevent editing since it's tied to the logged-in user */}
                    <Input
                      id="instructor"
                      value={CURRENT_FACULTY_ID}
                      className="col-span-3 bg-muted/50"
                      disabled
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="capacity" className="text-right">
                      Capacity
                    </Label>
                    <Input
                      id="capacity"
                      type="number"
                      value={formState.capacity}
                      onChange={handleFormChange}
                      className="col-span-3"
                      required
                      min={1}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">{editingCourse ? "Save Changes" : "Create Course"}</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Instructor</TableHead>
                <TableHead className="text-right">Capacity</TableHead>
                <TableHead className="text-center w-[120px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {courses.map((course) => {
                const isAuthorized = course.instructor === CURRENT_FACULTY_ID;
                return (
                  <TableRow key={course.id}>
                    <TableCell className="font-medium">{course.id}</TableCell>
                    <TableCell>{course.name}</TableCell>
                    <TableCell>{course.instructor}</TableCell>
                    <TableCell className="text-right">{course.capacity}</TableCell>
                    <TableCell className="flex justify-center space-x-2">
                      {isAuthorized ? (
                        <>
                          <Button variant="outline" size="icon" onClick={() => openEditDialog(course)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="destructive" size="icon" onClick={() => handleDeleteCourse(course.id, course.instructor)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </>
                      ) : (
                        <Button variant="ghost" size="icon" disabled title={`Managed by ${course.instructor}`}>
                            <Lock className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      )}
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

export default FacultyCourseManagement;