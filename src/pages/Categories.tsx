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

export default function Categories() {
  const [categories, setCategories] = useState<any[]>([]);
  const [newCategory, setNewCategory] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    const { data, error } = await supabase
      .from('categories')
      .select('*')
      .order('name');

    if (error) {
      toast.error("Ошибка загрузки категорий");
      return;
    }
    setCategories(data || []);
  };

  const handleAdd = async () => {
    if (!newCategory.trim()) return;

    const { error } = await supabase
      .from('categories')
      .insert({ name: newCategory.trim() });

    if (error) {
      toast.error("Ошибка добавления категории");
      return;
    }

    toast.success("Категория добавлена");
    setNewCategory("");
    fetchCategories();
  };

  const handleEdit = (id: string, name: string) => {
    setEditingId(id);
    setEditValue(name);
  };

  const handleSave = async (id: string) => {
    const { error } = await supabase
      .from('categories')
      .update({ name: editValue })
      .eq('id', id);

    if (error) {
      toast.error("Ошибка обновления");
      return;
    }

    toast.success("Категория обновлена");
    setEditingId(null);
    fetchCategories();
  };

  const handleDelete = async (id: string) => {
    const { error } = await supabase
      .from('categories')
      .delete()
      .eq('id', id);

    if (error) {
      toast.error("Ошибка удаления");
      return;
    }

    toast.success("Категория удалена");
    fetchCategories();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Категории</h1>
        <p className="text-muted-foreground">Управление категориями товаров</p>
      </div>

      <Card className="p-6">
        <div className="flex gap-2 mb-6">
          <Input
            placeholder="Название категории"
            value={newCategory}
            onChange={(e) => setNewCategory(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
          />
          <Button onClick={handleAdd}>Добавить</Button>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Название</TableHead>
              <TableHead className="w-[100px]">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {categories.map((cat) => (
              <TableRow key={cat.id}>
                <TableCell>
                  {editingId === cat.id ? (
                    <Input
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      autoFocus
                    />
                  ) : (
                    cat.name
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    {editingId === cat.id ? (
                      <>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleSave(cat.id)}
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
                          onClick={() => handleEdit(cat.id, cat.name)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleDelete(cat.id)}
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
