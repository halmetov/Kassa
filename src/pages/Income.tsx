import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Pencil, Trash2, Save, X } from "lucide-react";

export default function Income() {
  const [branches, setBranches] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [receipts, setReceipts] = useState<any[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editData, setEditData] = useState<any>({});
  
  const [formData, setFormData] = useState({
    branch_id: "",
    product_id: "",
    quantity: "",
    purchase_price: "",
    sale_price: "",
  });

  useEffect(() => {
    fetchBranches();
    fetchProducts();
    fetchReceipts();
  }, []);

  const fetchBranches = async () => {
    const { data, error } = await supabase
      .from("branches")
      .select("*")
      .eq("is_active", true)
      .order("name");
    
    if (error) {
      toast.error("Ошибка загрузки филиалов");
      return;
    }
    setBranches(data || []);
  };

  const fetchProducts = async () => {
    const { data, error } = await supabase
      .from("products")
      .select("*, categories(name)")
      .order("name");
    
    if (error) {
      toast.error("Ошибка загрузки товаров");
      return;
    }
    setProducts(data || []);
  };

  const fetchReceipts = async () => {
    const { data, error } = await supabase
      .from("stock_receipts")
      .select(`
        *,
        branches(name),
        products(name),
        employees(name)
      `)
      .order("created_at", { ascending: false });
    
    if (error) {
      toast.error("Ошибка загрузки истории");
      return;
    }
    setReceipts(data || []);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.branch_id || !formData.product_id || !formData.quantity || 
        !formData.purchase_price || !formData.sale_price) {
      toast.error("Заполните все поля");
      return;
    }

    const { data: { user } } = await supabase.auth.getUser();
    
    const { data: employee } = await supabase
      .from("employees")
      .select("id")
      .eq("user_id", user?.id)
      .single();

    const { error } = await supabase
      .from("stock_receipts")
      .insert({
        branch_id: formData.branch_id,
        product_id: formData.product_id,
        quantity: parseFloat(formData.quantity),
        purchase_price: parseFloat(formData.purchase_price),
        sale_price: parseFloat(formData.sale_price),
        employee_id: employee?.id,
      });

    if (error) {
      toast.error("Ошибка при добавлении прихода");
      return;
    }

    toast.success("Приход успешно добавлен");
    setFormData({
      branch_id: "",
      product_id: "",
      quantity: "",
      purchase_price: "",
      sale_price: "",
    });
    fetchReceipts();
  };

  const handleEdit = (receipt: any) => {
    setEditingId(receipt.id);
    setEditData({
      quantity: receipt.quantity,
      purchase_price: receipt.purchase_price,
      sale_price: receipt.sale_price,
    });
  };

  const handleSave = async (id: string) => {
    const { error } = await supabase
      .from("stock_receipts")
      .update({
        quantity: parseFloat(editData.quantity),
        purchase_price: parseFloat(editData.purchase_price),
        sale_price: parseFloat(editData.sale_price),
      })
      .eq("id", id);

    if (error) {
      toast.error("Ошибка при обновлении");
      return;
    }

    toast.success("Приход обновлен");
    setEditingId(null);
    fetchReceipts();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Вы уверены, что хотите удалить этот приход?")) return;

    const { error } = await supabase
      .from("stock_receipts")
      .delete()
      .eq("id", id);

    if (error) {
      toast.error("Ошибка при удалении");
      return;
    }

    toast.success("Приход удален");
    fetchReceipts();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Приход</h1>
        <p className="text-muted-foreground">Приход товаров на склад</p>
      </div>

      <Tabs defaultValue="receipt" className="w-full">
        <TabsList>
          <TabsTrigger value="receipt">Приход</TabsTrigger>
          <TabsTrigger value="history">История</TabsTrigger>
        </TabsList>

        <TabsContent value="receipt" className="space-y-4">
          <form onSubmit={handleAdd} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 p-4 border rounded-lg bg-card">
            <div className="space-y-2">
              <Label htmlFor="branch">Филиал</Label>
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

            <div className="space-y-2">
              <Label htmlFor="product">Товар</Label>
              <Select
                value={formData.product_id}
                onValueChange={(value) => setFormData({ ...formData, product_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите товар" />
                </SelectTrigger>
                <SelectContent>
                  {products.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      {product.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantity">Количество</Label>
              <Input
                id="quantity"
                type="number"
                step="0.01"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                placeholder="0"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="purchase_price">Цена прихода</Label>
              <Input
                id="purchase_price"
                type="number"
                step="0.01"
                value={formData.purchase_price}
                onChange={(e) => setFormData({ ...formData, purchase_price: e.target.value })}
                placeholder="0"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="sale_price">Цена продажи</Label>
              <Input
                id="sale_price"
                type="number"
                step="0.01"
                value={formData.sale_price}
                onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })}
                placeholder="0"
              />
            </div>

            <div className="flex items-end">
              <Button type="submit" className="w-full">
                Добавить приход
              </Button>
            </div>
          </form>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Филиал</TableHead>
                  <TableHead>Товар</TableHead>
                  <TableHead>Количество</TableHead>
                  <TableHead>Цена прихода</TableHead>
                  <TableHead>Цена продажи</TableHead>
                  <TableHead>Сотрудник</TableHead>
                  <TableHead>Дата</TableHead>
                  <TableHead>Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {receipts.map((receipt) => (
                  <TableRow key={receipt.id}>
                    <TableCell>{receipt.branches?.name}</TableCell>
                    <TableCell>{receipt.products?.name}</TableCell>
                    <TableCell>
                      {editingId === receipt.id ? (
                        <Input
                          type="number"
                          step="0.01"
                          value={editData.quantity}
                          onChange={(e) => setEditData({ ...editData, quantity: e.target.value })}
                          className="w-24"
                        />
                      ) : (
                        receipt.quantity
                      )}
                    </TableCell>
                    <TableCell>
                      {editingId === receipt.id ? (
                        <Input
                          type="number"
                          step="0.01"
                          value={editData.purchase_price}
                          onChange={(e) => setEditData({ ...editData, purchase_price: e.target.value })}
                          className="w-24"
                        />
                      ) : (
                        receipt.purchase_price
                      )}
                    </TableCell>
                    <TableCell>
                      {editingId === receipt.id ? (
                        <Input
                          type="number"
                          step="0.01"
                          value={editData.sale_price}
                          onChange={(e) => setEditData({ ...editData, sale_price: e.target.value })}
                          className="w-24"
                        />
                      ) : (
                        receipt.sale_price
                      )}
                    </TableCell>
                    <TableCell>{receipt.employees?.name || "-"}</TableCell>
                    <TableCell>
                      {new Date(receipt.created_at).toLocaleDateString("ru-RU")}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {editingId === receipt.id ? (
                          <>
                            <Button
                              size="icon"
                              variant="ghost"
                              onClick={() => handleSave(receipt.id)}
                            >
                              <Save className="h-4 w-4" />
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
                              onClick={() => handleEdit(receipt)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              onClick={() => handleDelete(receipt.id)}
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
        </TabsContent>
      </Tabs>
    </div>
  );
}
