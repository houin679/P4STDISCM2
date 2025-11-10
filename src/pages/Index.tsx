import Layout from "@/components/Layout";
import { useMockAuth } from "@/hooks/use-mock-auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Index = () => {
  const { userRole } = useMockAuth();

  let title = "Welcome to the Distributed Grade System";
  let description = "Please log in to access your features.";
  let actions = (
    <Button asChild size="lg">
      <Link to="/login">Go to Login</Link>
    </Button>
  );

  if (userRole === "student") {
    title = "Student Dashboard";
    description = "View your courses and grades.";
    actions = (
      <div className="flex gap-4">
        <Button asChild>
          <Link to="/courses">Choose Courses</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/grades">View Grades</Link>
        </Button>
      </div>
    );
  } else if (userRole === "faculty") {
    title = "Faculty Dashboard";
    description = "Manage grade submissions for your courses.";
    actions = (
      <Button asChild size="lg">
        <Link to="/faculty/upload">Upload Grades</Link>
      </Button>
    );
  }

  return (
    <Layout>
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-16rem)]">
        <Card className="w-full max-w-lg text-center">
          <CardHeader>
            <CardTitle className="text-4xl font-extrabold">{title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-xl text-muted-foreground">{description}</p>
            {actions}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Index;