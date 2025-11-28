import React, { useState } from "react";
import Layout from "@/components/Layout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { showSuccess, showError } from "@/utils/toast";
import { Plus, Trash2, Edit } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Navigate } from "react-router-dom";

interface Course {
  id: number;
  code: string;
  name: string;
  instructor: string;
  capacity: number;
}

const FacultyCourseManagement = () => {
  const { userRole } = useAuth();
  const qc = useQueryClient();
  const { data: courses = [], isLoading } = useQuery({
    queryKey: ['courses'], 
    queryFn: async () => {
      const res = await api.apiFetch('/api/courses');
      if (!res.ok) throw new Error('Failed to load courses');
      return res.json();
    }
  });
  const [formState, setFormState] = useState<Omit<Course, 'id'>>({
    code: "",
    name: "",
    instructor: "",
    capacity: 0,
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);

  // Redirect if not Course Audit Admin
  if (userRole !== "course_audit_admin") {
    showError("Access Denied: Only Course Audit Admins can manage the course catalog.");
    return <Navigate to="/" replace />;
  }

  React.useEffect(() => {
    if (editingCourse) {
      setFormState({ code: editingCourse.code, name: editingCourse.name, instructor: editingCourse.instructor, capacity: editingCourse.capacity });
    } else {
      setFormState({ code: "", name: "", instructor: "", capacity: 0 });
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

    if (!formState.code || !formState.name || !formState.instructor || formState.capacity <= 0) {
      showError("Please fill in all fields correctly.");
      return;
    }

    (async () => {
      try {
        if (editingCourse) {
          const res = await api.apiFetch(`/api/courses/${editingCourse.id}`, { 
            method: 'PUT', 
            body: JSON.stringify({ code: formState.code, name: formState.name, instructor: formState.instructor, capacity: formState.capacity }) 
          });
          if (!res.ok) { showError('Failed to update course'); return; }
          showSuccess(`Course ${formState.code} updated successfully!`);
        } else {
          const res = await api.apiFetch('/api/courses', { 
            method: 'POST', 
            body: JSON.stringify({ code: formState.code, name: formState.name, instructor: formState.instructor, capacity: formState.capacity }) 
          });
          if (!res.ok) { showError('Failed to create course'); return; }
          showSuccess(`Course ${formState.code} added successfully!`);
        }
        setIsDialogOpen(false);
        setEditingCourse(null);
        qc.invalidateQueries({ queryKey: ['courses'] });
      } catch (err) {
        showError('Failed to save course');
      }
    })();
  };

  const handleDeleteCourse = (courseId: number) => {
    (async () => {
      if (!confirm(`Are you sure you want to delete this course?`)) return;
      try {
        const res = await api.apiFetch(`/api/courses/${courseId}`, { method: 'DELETE' });
        if (!res.ok) { showError('Failed to delete course'); return; }
        showSuccess(`Course deleted successfully!`);
        qc.invalidateQueries({ queryKey: ['courses'] });
      } catch (err) { showError('Failed to delete course'); }
    })();
  };

  const openAddDialog = () => {
    setEditingCourse(null);
    setIsDialogOpen(true);
  };

  const openEditDialog = (course: Course) => {
    setEditingCourse(course);
    setIsDialogOpen(true);
  };

  if (userRole !== 'course_audit_admin') {
    showError('Access Denied: Only Course Audit Admins can manage the course catalog.');
    return <Navigate to="/" replace />;
  }

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">Course Catalog Management</h1>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-2xl font-bold">Current Courses</CardTitle>
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
                    <Label htmlFor="code" className="text-right">
                      Course Code
                    </Label>
                    <Input
                      id="code"
                      value={formState.code}
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
                    <Input
                      id="instructor"
                      value={formState.instructor}
                      onChange={handleFormChange}
                      className="col-span-3"
                      required
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
                <TableHead className="w-[100px]">Code</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Instructor</TableHead>
                <TableHead className="text-right">Capacity</TableHead>
                <TableHead className="text-center w-[120px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {courses.map((course) => (
                <TableRow key={course.id}>
                  <TableCell className="font-medium">{course.code}</TableCell>
                  <TableCell>{course.name}</TableCell>
                  <TableCell>{course.instructor}</TableCell>
                  <TableCell className="text-right">{course.capacity}</TableCell>
                  <TableCell className="flex justify-center space-x-2">
                    <Button variant="outline" size="icon" onClick={() => openEditDialog(course)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="destructive" size="icon" onClick={() => handleDeleteCourse(course.id)}>
                      <Trash2 className="h-4 w-4" />
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

export default FacultyCourseManagement;