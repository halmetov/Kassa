import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
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

export default function Clients() {
  const [clients, setClients] = useState<any[]>([]);
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [newDebt, setNewDebt] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editPhone, setEditPhone] = useState("");
  const [editDebt, setEditDebt] = useState("");

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    const { data, error } = await supabase
      .from('clients')
      .select('*')
      .order('name');

    if (error) {
      toast.error("Ошибка загрузки клиентов");
      return;
    }
    setClients(data || []);
  };

  const handleAdd = async () => {
    if (!newName.trim()) return;

    const { error } = await supabase
      .from('clients')
      .insert({ 
        name: newName.trim(),
        phone: newPhone.trim() || null,
        debt: newDebt ? parseFloat(newDebt) : 0
      });

    if (error) {
      toast.error("Ошибка добавления клиента");
      return;
    }

    toast.success("Клиент добавлен");
    setNewName("");
    setNewPhone("");
    setNewDebt("");
    fetchClients();
  };

  const handleEdit = (client: any) => {
    setEditingId(client.id);
    setEditName(client.name);
    setEditPhone(client.phone || "");
    setEditDebt(client.debt?.toString() || "0");
  };

  const handleSave = async (id: string) => {
    const { error } = await supabase
      .from('clients')
      .update({ 
        name: editName, 
        phone: editPhone || null,
        debt: editDebt ? parseFloat(editDebt) : 0
      })
      .eq('id', id);

    if (error) {
      toast.error("Ошибка обновления");
      return;
    }

    toast.success("Клиент обновлен");
    setEditingId(null);
    fetchClients();
  };

  const handleDelete = async (id: string) => {
    const { error } = await supabase
      .from('clients')
      .delete()
      .eq('id', id);

    if (error) {
      toast.error("Ошибка удаления");
      return;
    }

    toast.success("Клиент удален");
    fetchClients();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Клиенты</h1>
        <p className="text-muted-foreground">Управление клиентами</p>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Input
            placeholder="Имя клиента"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
          />
          <Input
            placeholder="Телефон"
            value={newPhone}
            onChange={(e) => setNewPhone(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
          />
          <Input
            placeholder="Долг"
            type="number"
            value={newDebt}
            onChange={(e) => setNewDebt(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
          />
          <Button onClick={handleAdd} className="md:col-span-3">Добавить</Button>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Имя</TableHead>
              <TableHead>Телефон</TableHead>
              <TableHead>Долг</TableHead>
              <TableHead className="w-[100px]">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {clients.map((client) => (
              <TableRow key={client.id}>
                <TableCell>
                  {editingId === client.id ? (
                    <Input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      autoFocus
                    />
                  ) : (
                    client.name
                  )}
                </TableCell>
                <TableCell>
                  {editingId === client.id ? (
                    <Input
                      value={editPhone}
                      onChange={(e) => setEditPhone(e.target.value)}
                      placeholder="Телефон"
                    />
                  ) : (
                    client.phone || "-"
                  )}
                </TableCell>
                <TableCell>
                  {editingId === client.id ? (
                    <Input
                      type="number"
                      value={editDebt}
                      onChange={(e) => setEditDebt(e.target.value)}
                      placeholder="Долг"
                    />
                  ) : (
                    <span className={client.debt > 0 ? "text-destructive" : ""}>
                      {client.debt || 0}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    {editingId === client.id ? (
                      <>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleSave(client.id)}
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
                          onClick={() => handleEdit(client)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleDelete(client.id)}
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
