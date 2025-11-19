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

interface Product {
  id: string;
  name: string;
  category_id: string | null;
  unit: string;
  barcode: string | null;
  purchase_price: number;
  sale_price: number;
  wholesale_price: number;
  limit_quantity: number;
  quantity: number;
  categories?: { name: string };
}

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: "",
    category_id: "",
    unit: "шт",
    barcode: "",
    purchase_price: "0",
    sale_price: "0",
    wholesale_price: "0",
    limit_quantity: "0",
  });

  const [editData, setEditData] = useState<any>({});

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  const fetchProducts = async () => {
    const { data, error } = await supabase
      .from('products')
      .select(`
        *,
        categories (name)
      `)
      .order('name');

    if (error) {
      toast.error("Ошибка загрузки товаров");
      return;
    }
    setProducts(data || []);
  };

  const fetchCategories = async () => {
    const { data, error } = await supabase
      .from('categories')
      .select('*')
      .order('name');

    if (error) return;
    setCategories(data || []);
  };

  const handleAdd = async () => {
    if (!formData.name.trim()) {
      toast.error("Введите название товара");
      return;
    }

    const { error } = await supabase.from('products').insert({
      name: formData.name.trim(),
      category_id: formData.category_id || null,
      unit: formData.unit,
      barcode: formData.barcode || null,
      purchase_price: parseFloat(formData.purchase_price) || 0,
      sale_price: parseFloat(formData.sale_price) || 0,
      wholesale_price: parseFloat(formData.wholesale_price) || 0,
      limit_quantity: parseInt(formData.limit_quantity) || 0,
    });

    if (error) {
      toast.error("Ошибка добавления товара");
      return;
    }

    toast.success("Товар добавлен");
    setFormData({
      name: "",
      category_id: "",
      unit: "шт",
      barcode: "",
      purchase_price: "0",
      sale_price: "0",
      wholesale_price: "0",
      limit_quantity: "0",
    });
    fetchProducts();
  };

  const handleEdit = (product: Product) => {
    setEditingId(product.id);
    setEditData({
      name: product.name,
      category_id: product.category_id || "",
      unit: product.unit,
      barcode: product.barcode || "",
      purchase_price: product.purchase_price.toString(),
      sale_price: product.sale_price.toString(),
      wholesale_price: product.wholesale_price.toString(),
      limit_quantity: product.limit_quantity.toString(),
    });
  };

  const handleSave = async (id: string) => {
    const { error } = await supabase
      .from('products')
      .update({
        name: editData.name,
        category_id: editData.category_id || null,
        unit: editData.unit,
        barcode: editData.barcode || null,
        purchase_price: parseFloat(editData.purchase_price) || 0,
        sale_price: parseFloat(editData.sale_price) || 0,
        wholesale_price: parseFloat(editData.wholesale_price) || 0,
        limit_quantity: parseInt(editData.limit_quantity) || 0,
      })
      .eq('id', id);

    if (error) {
      toast.error("Ошибка обновления");
      return;
    }

    toast.success("Товар обновлен");
    setEditingId(null);
    fetchProducts();
  };

  const handleDelete = async (id: string) => {
    const { error } = await supabase
      .from('products')
      .delete()
      .eq('id', id);

    if (error) {
      toast.error("Ошибка удаления");
      return;
    }

    toast.success("Товар удален");
    fetchProducts();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Товары</h1>
        <p className="text-muted-foreground">Управление товарами</p>
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Добавить товар</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <Label>Название</Label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Название товара"
            />
          </div>
          <div>
            <Label>Категория</Label>
            <Select
              value={formData.category_id}
              onValueChange={(value) => setFormData({ ...formData, category_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Без категории" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((cat) => (
                  <SelectItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Ед. измерения</Label>
            <Input
              value={formData.unit}
              onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
              placeholder="шт, кг, л"
            />
          </div>
          <div>
            <Label>Штрих-код</Label>
            <Input
              value={formData.barcode}
              onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
              placeholder="Штрих-код"
            />
          </div>
          <div>
            <Label>Цена прихода</Label>
            <Input
              type="number"
              value={formData.purchase_price}
              onChange={(e) => setFormData({ ...formData, purchase_price: e.target.value })}
            />
          </div>
          <div>
            <Label>Цена продажи</Label>
            <Input
              type="number"
              value={formData.sale_price}
              onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })}
            />
          </div>
          <div>
            <Label>Цена оптом</Label>
            <Input
              type="number"
              value={formData.wholesale_price}
              onChange={(e) => setFormData({ ...formData, wholesale_price: e.target.value })}
            />
          </div>
          <div>
            <Label>Лимит</Label>
            <Input
              type="number"
              value={formData.limit_quantity}
              onChange={(e) => setFormData({ ...formData, limit_quantity: e.target.value })}
            />
          </div>
        </div>
        <Button onClick={handleAdd}>Добавить товар</Button>
      </Card>

      <Card className="p-6">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Название</TableHead>
                <TableHead>Категория</TableHead>
                <TableHead>Ед.изм</TableHead>
                <TableHead>Штрих-код</TableHead>
                <TableHead>Приход</TableHead>
                <TableHead>Продажа</TableHead>
                <TableHead>Оптом</TableHead>
                <TableHead>Лимит</TableHead>
                <TableHead>Кол-во</TableHead>
                <TableHead className="w-[100px]">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id}>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        value={editData.name}
                        onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                      />
                    ) : (
                      product.name
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Select
                        value={editData.category_id}
                        onValueChange={(value) => setEditData({ ...editData, category_id: value })}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map((cat) => (
                            <SelectItem key={cat.id} value={cat.id}>
                              {cat.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      product.categories?.name || "Без категории"
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        value={editData.unit}
                        onChange={(e) => setEditData({ ...editData, unit: e.target.value })}
                        className="w-20"
                      />
                    ) : (
                      product.unit
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        value={editData.barcode}
                        onChange={(e) => setEditData({ ...editData, barcode: e.target.value })}
                      />
                    ) : (
                      product.barcode || "-"
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        type="number"
                        value={editData.purchase_price}
                        onChange={(e) => setEditData({ ...editData, purchase_price: e.target.value })}
                        className="w-24"
                      />
                    ) : (
                      product.purchase_price
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        type="number"
                        value={editData.sale_price}
                        onChange={(e) => setEditData({ ...editData, sale_price: e.target.value })}
                        className="w-24"
                      />
                    ) : (
                      product.sale_price
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        type="number"
                        value={editData.wholesale_price}
                        onChange={(e) => setEditData({ ...editData, wholesale_price: e.target.value })}
                        className="w-24"
                      />
                    ) : (
                      product.wholesale_price
                    )}
                  </TableCell>
                  <TableCell>
                    {editingId === product.id ? (
                      <Input
                        type="number"
                        value={editData.limit_quantity}
                        onChange={(e) => setEditData({ ...editData, limit_quantity: e.target.value })}
                        className="w-20"
                      />
                    ) : (
                      product.limit_quantity
                    )}
                  </TableCell>
                  <TableCell className={product.quantity <= product.limit_quantity ? "text-destructive font-semibold" : ""}>
                    {product.quantity}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      {editingId === product.id ? (
                        <>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => handleSave(product.id)}
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
                            onClick={() => handleEdit(product)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => handleDelete(product.id)}
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
        </div>
      </Card>
    </div>
  );
}
