import React from "react";
import Header from "./Header";
import { MadeWithDyad } from "./made-with-dyad";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-grow container py-8">{children}</main>
      <MadeWithDyad />
    </div>
  );
};

export default Layout;