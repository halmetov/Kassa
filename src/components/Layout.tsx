import { useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { getCurrentUser, getEmployeeByUserId } from "@/lib/auth";

export const Layout = () => {
  const [open, setOpen] = useState(true);
  const [employee, setEmployee] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const user = await getCurrentUser();
      if (!user) {
        navigate('/auth');
        return;
      }
      
      const emp = await getEmployeeByUserId(user.id);
      setEmployee(emp);
    };
    
    checkAuth();
  }, [navigate]);

  return (
    <SidebarProvider open={open} onOpenChange={setOpen}>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar employee={employee} />
        <main className="flex-1 flex flex-col">
          <header className="h-14 border-b bg-card flex items-center px-4 lg:px-6 lg:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setOpen(!open)}
            >
              <Menu className="h-5 w-5" />
            </Button>
          </header>
          <div className="flex-1 p-4 lg:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};
