import React from "react";

export type UserRole = "unauthenticated" | "student" | "faculty";

interface MockAuthContextType {
  userRole: UserRole;
  login: (role: UserRole) => void;
  logout: () => void;
}

const MockAuthContext = React.createContext<MockAuthContextType | undefined>(
  undefined,
);

export const MockAuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [userRole, setUserRole] = React.useState<UserRole>("unauthenticated");

  const login = (role: UserRole) => {
    setUserRole(role);
  };

  const logout = () => {
    setUserRole("unauthenticated");
  };

  return (
    <MockAuthContext.Provider value={{ userRole, login, logout }}>
      {children}
    </MockAuthContext.Provider>
  );
};

export const useMockAuth = () => {
  const context = React.useContext(MockAuthContext);
  if (context === undefined) {
    throw new Error("useMockAuth must be used within a MockAuthProvider");
  }
  return context;
};