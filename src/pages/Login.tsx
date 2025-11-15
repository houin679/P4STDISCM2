import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Layout from "@/components/Layout";
import { useMockAuth, UserRole } from "@/hooks/use-mock-auth";
import { showSuccess } from "@/utils/toast";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useMockAuth();
  const [selectedRole, setSelectedRole] = useState<UserRole>("student");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, we would validate credentials here.
    // For now, we simulate a successful login based on the selected role.
    login(selectedRole);
    showSuccess(`Successfully logged in as ${selectedRole}!`);
    navigate("/");
  };

  return (
    <Layout>
      <div className="flex justify-center items-center min-h-[calc(100vh-16rem)]">
        <Card className="w-[350px]">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl">Sign In</CardTitle>
            <CardDescription>
              Enter your credentials to access the system.
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleLogin}>
            <CardContent className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="id">Student/Faculty ID</Label>
                <Input id="id" type="text" placeholder="e.g., 12345 or F9876" required />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" required />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="role">Simulate Role</Label>
                <Select
                  value={selectedRole}
                  onValueChange={(value: UserRole) => setSelectedRole(value)}
                >
                  <SelectTrigger id="role">
                    <SelectValue placeholder="Select Role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="student">Student</SelectItem>
                    <SelectItem value="faculty">Faculty</SelectItem>
                    <SelectItem value="course_audit_admin">Course Audit Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" className="w-full">
                Login
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </Layout>
  );
};

export default Login;