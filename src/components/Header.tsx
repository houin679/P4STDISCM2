import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { LogIn, LogOut, BookOpen, GraduationCap, Upload, LayoutList } from "lucide-react";

const Header = () => {
  const { userRole, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navLinks = [
    {
      path: "/courses",
      label: "Courses",
      icon: BookOpen,
      roles: ["student"],
    },
    {
      path: "/grades",
      label: "Grades",
      icon: GraduationCap,
      roles: ["student"],
    },
    {
      path: "/faculty/upload",
      label: "Grade Upload",
      icon: Upload,
      roles: ["faculty"],
    },
    {
      path: "/faculty/courses",
      label: "Course Management",
      icon: LayoutList,
      roles: ["course_audit_admin"],
    },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="text-xl font-bold tracking-tight">
          Distributed Grade System
        </Link>
        <nav className="flex items-center space-x-4">
          {navLinks
            .filter((link) => link.roles.includes(userRole))
            .map((link) => (
              <Button key={link.path} variant="ghost" asChild>
                <Link to={link.path} className="flex items-center gap-2">
                  <link.icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{link.label}</span>
                </Link>
              </Button>
            ))}

          {userRole === "unauthenticated" ? (
            <Button asChild>
              <Link to="/login" className="flex items-center gap-2">
                <LogIn className="h-4 w-4" />
                Login
              </Link>
            </Button>
          ) : (
            <Button variant="outline" onClick={handleLogout} className="flex items-center gap-2">
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;