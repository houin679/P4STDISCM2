import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Layout from "@/components/Layout";
import { useAuth } from "@/hooks/use-auth";
import { showSuccess, showError } from "@/utils/toast";

type UserRole = "unauthenticated" | "student" | "faculty" | "course_audit_admin";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [idValue, setIdValue] = useState("");
  const [passwordValue, setPasswordValue] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const ok = await login(idValue, passwordValue);
      if (!ok) {
        showError('Login failed. Check credentials.');
        return;
      }
      showSuccess('Logged in successfully');
      navigate('/');
    } catch (err) {
      showError('Login failed');
    }
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
                <Input id="id" type="text" placeholder="e.g., student1" required value={idValue} onChange={(e) => setIdValue(e.target.value)} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" required value={passwordValue} onChange={(e) => setPasswordValue(e.target.value)} />
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