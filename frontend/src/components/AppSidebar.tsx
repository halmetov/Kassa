import { NavLink } from "@/components/NavLink";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  TrendingDown,
  Package,
  ShoppingCart,
  Warehouse,
  RotateCcw,
  BarChart3,
  Settings,
  FileText,
  Users,
  Building2,
  Tags,
  LogOut,
  UserCircle,
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronRight } from "lucide-react";
import { AuthUser, signOut } from "@/lib/auth";
import { toast } from "sonner";

const menuItems = [
  { title: "Приход", url: "/income", icon: TrendingDown },
  { title: "Склад", url: "/warehouse", icon: Warehouse },
  { title: "Касса", url: "/pos", icon: ShoppingCart },
  { title: "Отчет", url: "/reports", icon: FileText },
  { title: "Возврат", url: "/returns", icon: RotateCcw },
  { title: "Анализ", url: "/analysis", icon: BarChart3 },
];

const systemItems = [
  { title: "Категории", url: "/categories", icon: Tags, adminOnly: false },
  { title: "Товары", url: "/products", icon: Package, adminOnly: false },
  { title: "Сотрудники", url: "/employees", icon: Users, adminOnly: true },
  { title: "Филиалы", url: "/branches", icon: Building2, adminOnly: true },
  { title: "Клиенты", url: "/clients", icon: UserCircle, adminOnly: false },
];

export function AppSidebar({ user }: { user: AuthUser | null }) {
  const { open } = useSidebar();
  const location = useLocation();
  const navigate = useNavigate();
  const currentPath = location.pathname;

  const isSystemActive = systemItems.some((item) => currentPath === item.url);
  const isAdmin = user?.role === 'admin';

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/auth');
      toast.success("Вы вышли из системы");
    } catch (error) {
      toast.error("Ошибка при выходе");
    }
  };

  return (
    <Sidebar collapsible="icon" className="border-r">
      <SidebarContent>
        <div className="p-4 border-b">
          {open && (
            <h2 className="text-lg font-bold text-sidebar-foreground">POS Система</h2>
          )}
        </div>

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      className="hover:bg-sidebar-accent"
                      activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    >
                      <item.icon className="h-4 w-4" />
                      {open && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <Collapsible defaultOpen={isSystemActive} className="group/collapsible">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="hover:bg-sidebar-accent">
                <Settings className="h-4 w-4" />
                {open && (
                  <>
                    <span>Система</span>
                    <ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90 h-4 w-4" />
                  </>
                )}
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {systemItems
                    .filter((item) => !item.adminOnly || isAdmin)
                    .map((item) => (
                      <SidebarMenuItem key={item.title}>
                        <SidebarMenuButton asChild>
                          <NavLink
                            to={item.url}
                            className="hover:bg-sidebar-accent"
                            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                          >
                            <item.icon className="h-4 w-4" />
                            {open && <span>{item.title}</span>}
                          </NavLink>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>

        <SidebarGroup className="mt-auto">
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                  {open && <span>Выход</span>}
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
