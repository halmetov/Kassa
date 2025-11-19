import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Pencil, Trash2, Check, X } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

export default function Employees() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: "",
    username: "",
    password: "",
    role: "employee" as "admin" | "employee",
    branch_id: "",
    is_active: true,
  });

  const [editData, setEditData] = useState<any>({});

  useEffect(() => {
    fetchEmployees();
    fetchBranches();
  }, []);

  const fetchEmployees = async () => {
    const { data, error } = await supabase
      .from('employees')
      .select('*, branches(name)')
      .order('name');

    if (error) {
      toast.error("Ошибка загрузки сотрудников");
      return;
    }
    setEmployees(data || []);
  };

  const fetchBranches = async () => {
    const { data, error } = await supabase
      .from('branches')
      .select('*')
      .eq('is_active', true)
      .order('name');

    if (error) {
      toast.error("Ошибка загрузки филиалов");
      return;
    }
    setBranches(data || []);
  };

  const handleAdd = async () => {
    if (!formData.name.trim() || !formData.username.trim() || !formData.password.trim()) {
      toast.error("Заполните все поля");
      return;
    }

    const email = `${formData.username}@pos.local`;
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password: formData.password,
      options: {
        data: { name: formData.name },
      },
    });

    if (authError) {
      toast.error("Ошибка создания пользователя");
      return;
    }

    if (authData.user) {
      const { error } = await supabase.from('employees').insert({
        user_id: authData.user.id,
        name: formData.name.trim(),
        username: formData.username.trim(),
        role: formData.role,
        branch_id: formData.branch_id || null,
        is_active: formData.is_active,
      });

      if (error) {
        toast.error("Ошибка добавления сотрудника");
        return;
      }

      toast.success("Сотрудник добавлен");
      setFormData({
        name: "",
        username: "",
        password: "",
        role: "employee",
        branch_id: "",
        is_active: true,
      });
      fetchEmployees();
    }
  };

  const handleEdit = (employee: any) => {
    setEditingId(employee.id);
    setEditData({
      name: employee.name,
      username: employee.username,
      role: employee.role,
      branch_id: employee.branch_id || "",
      is_active: employee.is_active,
    });
  };

  const handleSave = async (id: string) => {
    const { error } = await supabase
      .from('employees')
      .update({
        name: editData.name,
        username: editData.username,
        role: editData.role,
        branch_id: editData.branch_id || null,
        is_active: editData.is_active,
      })
      .eq('id', id);

    if (error) {
      toast.error("Ошибка обновления");
      return;
    }

    toast.success("Сотрудник обновлен");
    setEditingId(null);
    fetchEmployees();
  };

  const handleDelete = async (id: string) => {
    const { error } = await supabase
      .from('employees')
      .delete()
      .eq('id', id);

    if (error) {
      toast.error("Ошибка удаления");
      return;
    }

    toast.success("Сотрудник удален");
    fetchEmployees();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Сотрудники</h1>
        <p className="text-muted-foreground">Управление сотрудниками</p>
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Добавить сотрудника</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-4">
          <div>
            <Label>Имя</Label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Имя сотрудника"
            />
          </div>
          <div>
            <Label>Логин</Label>
            <Input
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="Логин"
            />
          </div>
          <div>
            <Label>Пароль</Label>
            <Input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Пароль"
            />
          </div>
          <div>
            <Label>Роль</Label>
            <Select
              value={formData.role}
              onValueChange={(value: "admin" | "employee") => setFormData({ ...formData, role: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="employee">Сотрудник</SelectItem>
                <SelectItem value="admin">Админ</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Филиал</Label>
            <Select
              value={formData.branch_id}
              onValueChange={(value) => setFormData({ ...formData, branch_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Выберите филиал" />
              </SelectTrigger>
              <SelectContent>
                {branches.map((branch) => (
                  <SelectItem key={branch.id} value={branch.id}>
                    {branch.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end">
            <div className="flex items-center space-x-2">
              <Switch
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
              />
              <Label>Активен</Label>
            </div>
          </div>
        </div>
        <Button onClick={handleAdd}>Добавить сотрудника</Button>
      </Card>

      <Card className="p-6">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Имя</TableHead>
              <TableHead>Логин</TableHead>
              <TableHead>Роль</TableHead>
              <TableHead>Филиал</TableHead>
              <TableHead>Активность</TableHead>
              <TableHead className="w-[100px]">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {employees.map((emp) => (
              <TableRow key={emp.id}>
                <TableCell>
                  {editingId === emp.id ? (
                    <Input
                      value={editData.name}
                      onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    />
                  ) : (
                    emp.name
                  )}
                </TableCell>
                <TableCell>
                  {editingId === emp.id ? (
                    <Input
                      value={editData.username}
                      onChange={(e) => setEditData({ ...editData, username: e.target.value })}
                    />
                  ) : (
                    emp.username
                  )}
                </TableCell>
                <TableCell>
                  {editingId === emp.id ? (
                    <Select
                      value={editData.role}
                      onValueChange={(value) => setEditData({ ...editData, role: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="employee">Сотрудник</SelectItem>
                        <SelectItem value="admin">Админ</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <span>{emp.role === 'admin' ? 'Админ' : 'Сотрудник'}</span>
                  )}
                </TableCell>
                <TableCell>
                  {editingId === emp.id ? (
                    <Select
                      value={editData.branch_id || ""}
                      onValueChange={(value) => setEditData({ ...editData, branch_id: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите филиал" />
                      </SelectTrigger>
                      <SelectContent>
                        {branches.map((branch) => (
                          <SelectItem key={branch.id} value={branch.id}>
                            {branch.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    emp.branches?.name || "-"
                  )}
                </TableCell>
                <TableCell>
                  {editingId === emp.id ? (
                    <Switch
                      checked={editData.is_active}
                      onCheckedChange={(checked) => setEditData({ ...editData, is_active: checked })}
                    />
                  ) : (
                    <span className={emp.is_active ? "text-success" : "text-muted-foreground"}>
                      {emp.is_active ? "Активен" : "Неактивен"}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    {editingId === emp.id ? (
                      <>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleSave(emp.id)}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => setEditingId(null)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleEdit(emp)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleDelete(emp.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
