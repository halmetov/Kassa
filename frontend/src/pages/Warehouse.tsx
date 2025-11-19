import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AlertCircle } from "lucide-react";

export default function Warehouse() {
  const [branches, setBranches] = useState<any[]>([]);
  const [selectedBranch, setSelectedBranch] = useState("");
  const [stock, setStock] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBranches();
  }, []);

  useEffect(() => {
    if (selectedBranch) {
      fetchStock();
    }
  }, [selectedBranch]);

  const fetchBranches = async () => {
    const { data } = await supabase
      .from('branches')
      .select('*')
      .eq('is_active', true)
      .order('name');
    
    if (data) {
      setBranches(data);
      if (data.length > 0) {
        setSelectedBranch(data[0].id);
      }
    }
  };

  const fetchStock = async () => {
    setLoading(true);
    
    const { data: products } = await supabase
      .from('products')
      .select(`
        *,
        categories (name)
      `)
      .order('name');

    if (products) {
      setStock(products);
    }
    
    setLoading(false);
  };

  const isLowStock = (product: any) => {
    return product.quantity <= (product.limit_quantity || 0);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Склад</h1>
        <p className="text-muted-foreground">Остатки товаров</p>
      </div>

      <Card className="p-6">
        <div className="mb-6">
          <Label>Филиал</Label>
          <Select value={selectedBranch} onValueChange={setSelectedBranch}>
            <SelectTrigger className="w-full md:w-64">
              <SelectValue placeholder="Выберите филиал" />
            </SelectTrigger>
            <SelectContent>
              {branches.map(branch => (
                <SelectItem key={branch.id} value={branch.id}>
                  {branch.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {loading ? (
          <div className="text-center py-8 text-muted-foreground">
            Загрузка...
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Товар</TableHead>
                <TableHead>Категория</TableHead>
                <TableHead>Штрихкод</TableHead>
                <TableHead className="text-right">Количество</TableHead>
                <TableHead className="text-right">Лимит</TableHead>
                <TableHead className="text-right">Цена продажи</TableHead>
                <TableHead>Статус</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stock.map((product) => (
                <TableRow 
                  key={product.id}
                  className={isLowStock(product) ? "bg-destructive/10" : ""}
                >
                  <TableCell className="font-medium">{product.name}</TableCell>
                  <TableCell>{product.categories?.name || "-"}</TableCell>
                  <TableCell className="font-mono text-sm">
                    {product.barcode || "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    {product.quantity || 0} {product.unit}
                  </TableCell>
                  <TableCell className="text-right">
                    {product.limit_quantity || 0}
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {product.sale_price} ₸
                  </TableCell>
                  <TableCell>
                    {isLowStock(product) && (
                      <div className="flex items-center gap-1 text-destructive">
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-sm">Мало на складе</span>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
